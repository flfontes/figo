from time import sleep

from pydantic import BaseModel

from figo.etl.extraction.webscraper import Scraper
from figo.etl.loading.database import Database
from figo.logger.config import logger as log
from figo.settings.config import Settings


class Player(BaseModel):
    name: str
    code: str
    link: str


class PlayerList:
    def __init__(self, database: Database, scraper: Scraper, settings: Settings) -> None:
        self.database: Database = database
        self.scraper: Scraper = scraper
        self.settings: Settings = settings

    def get_players(self) -> list[Player]:
        landing_page_html = self.scraper.request_blocking(self.settings.players_url)

        landing_page_elements = self.scraper.parse(
            landing_page_html, 'ul.page_index li div a'
        )

        landing_page_links = [
            self.scraper.extract_links(element) for element in landing_page_elements
        ]

        players_list: list[Player] = []
        for link in landing_page_links:
            url_players_page = self.settings.base_url + link

            player_page_html = self.scraper.request_blocking(url_players_page)

            player_page_elements = self.scraper.parse(
                player_page_html, 'div.section_content p a'
            )

            for element in player_page_elements:
                player_link = self.scraper.extract_links(element)

                link_components = player_link.split('/')

                player_name = link_components[-1].replace('-', ' ')
                if player_name == '':
                    log.debug('Player name not valid. Element excluded correctly.')
                    continue

                player_code = link_components[-2]

                players_list.append(
                    Player(
                        name=player_name,
                        code=player_code,
                        link=player_link,
                    )
                )

            sleep(2)

        return players_list


class PlayerStats(BaseModel):
    name: str


class PlayersStatsList:
    pass


if __name__ == '__main__':
    pass
