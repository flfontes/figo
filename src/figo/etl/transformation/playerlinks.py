from typing import Iterator

from pydantic import BaseModel
from sqlalchemy import select, update

from figo.etl.extraction.webscraper import Scraper
from figo.etl.loading.database import Database
from figo.etl.loading.models import PlayerLinkDB
from figo.logger.config import logger as log
from figo.settings.config import Settings


class PlayerLinkValidation(BaseModel):
    name: str
    name_code: str
    code: str
    link: str


class PlayerLink:
    def __init__(
        self,
        database: Database,
        scraper: Scraper,
        settings: Settings,
    ) -> None:
        self.database: Database = database
        self.scraper: Scraper = scraper
        self.settings: Settings = settings


    def _get_landing_page_links(self) -> Iterator:
        landing_page_html = self.scraper.request_blocking(
            self.settings.players_url
        )
        log.debug(f'HTML: \n{landing_page_html}')

        landing_page_elements = self.scraper.parse(
            landing_page_html,
            'ul.page_index li div a'
        )
        log.debug(f'Elements: \n{landing_page_elements}')

        return [
            self.scraper.extract_links(element) 
            for element in landing_page_elements
        ]


    def _get_player_link(self) -> Iterator:
        for link in self._get_landing_page_links():
            log.debug(f'Link: {link}.')
            url_players_page = self.settings.base_url + link

            players_page_html = self.scraper.request_blocking(
                url_players_page
            )

            players_page_elements = self.scraper.parse(
                players_page_html,
                'div.section_content p a'
            )

            yield [
                self.scraper.extract_links(element)
                for element in players_page_elements
            ]


    def _parse_player_link(self) -> Iterator:
        for links in self._get_player_link():
            for player_link in links:

                log.debug(f'Link: {player_link}.')
                link_components = player_link.split('/')

                player_name_code = link_components[-1]

                player_name = player_name_code.replace('-', ' ')

                if player_name == '':
                    log.debug('Not a player. Element was exluded successfully.')
                    continue

                player_code = link_components[-2]

                yield PlayerLinkValidation(
                    name=player_name,
                    name_code=player_name_code,
                    code=player_code,
                    link=self.settings.base_url + player_link
                )

    def sink_player_link_to_database(self) -> None:
        with self.database.get_session() as session:
            for player in self._parse_player_link():

                log.debug(player)
                stmt = select(PlayerLinkDB).where(PlayerLinkDB.code == player.code)

                player_in_db = session.execute(stmt).scalar()

                if player_in_db is not None:
                    update_stmt = (
                        update(PlayerLinkDB)
                        .where(PlayerLinkDB.code == player.code)
                        .values(
                            name=player.name,
                            name_code=player.name_code,
                            link=player.link
                        )
                    )

                    session.execute(update_stmt)

                else:
                    session.add(
                        PlayerLinkDB(
                            name = player.name,
                            name_code = player.name_code,
                            code = player.code,
                            link = player.link
                        )
                    )

                    session.commit()
