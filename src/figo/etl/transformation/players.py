from datetime import date, datetime
from time import sleep

from pydantic import BaseModel
from sqlalchemy import select

from figo.etl.extraction.webscraper import Scraper
from figo.etl.loading.database import Database
from figo.etl.loading.models import DBPlayerLink, DBPlayerMetadata
from figo.logger.config import logger as log
from figo.settings.config import Settings


class Player(BaseModel):
    name: str
    code: str
    link: str


class PlayerMetadata(BaseModel):
    name: str
    code: str
    fullname: str
    height: int
    weight: int
    nationality: str
    birthday: date
    preferred_foot: str
    position: str
    current_club: str
    national_team: str


class AvailablePlayer:
    def __init__(
        self, database: Database, scraper: Scraper, settings: Settings
    ) -> None:
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
                        link=self.settings.base_url + player_link,
                    )
                )

            sleep(2)

        return players_list

    def sink_to_db(self) -> None:
        with self.database.get_session() as session:
            for player in self.get_players():
                dbplayer = DBPlayerLink(
                    name=player.name,
                    code=player.code,
                    link=player.link,
                )
                session.add(dbplayer)

            session.commit()


class PlayerStatsList:
    def __init__(
        self, database: Database, scraper: Scraper, settings: Settings
    ) -> None:
        self.database: Database = database
        self.scraper: Scraper = scraper
        self.settings: Settings = settings

    def get_player_metadata(self, player_code: str) -> PlayerMetadata:
        with self.database.get_session() as session:
            stmt = select(DBPlayerLink).where(DBPlayerLink.code == player_code)
            log.debug(f'SQL statment to start metadata scraper:\n {stmt}')

            player = session.execute(stmt).first()

        name = player[0].name
        link = player[0].link

        log.debug(f'Scraping metadata for {name}')

        player_page = self.scraper.request_blocking(link)

        player_page_elements = self.scraper.parse(player_page, 'div#meta div p')

        # player_metadata_raw = [
        #     element.text() for element in player_page_elements
        # ]

        player_metadata_raw = []
        for element in player_page_elements:

            log.debug(element.text())

            if element.text().strip()[0] in ['1', '2']:
                height_weight = [value.text() for value in element.css('span')]
                log.debug(height_weight)

                for index, value in enumerate(height_weight):
                    if value.endswith('cm'):
                        height_weight[index] = 'Height: ' + value.replace('cm', '')
                    if value.endswith('kg'):
                        height_weight[index] = 'Weight: ' + value.replace('kg', '')

                player_metadata_raw.extend(height_weight)
                log.debug(height_weight)

            if element.text().strip().startswith('Born'):
                birthdate = element.css_first('span')
                try:
                    player_metadata_raw.append('Born:' + birthdate.attributes['data-birth'])
                    log.debug(birthdate)
                except KeyError:
                    birthdate = datetime.strptime(
                        birthdate
                        .text()
                        .strip(), '%B %d, %Y'
                    ).strftime('Born: %Y-%m-%d')
                    player_metadata_raw.append(birthdate)
                    log.debug(birthdate)

            elif element.text().strip().startswith('Position'):
                position_footed = element.text().split(' ▪  ')
                player_metadata_raw.extend(position_footed)
                log.debug(position_footed)

            else:
                player_metadata_raw.append(element.text())
                log.debug(element.text())


        player_metadata = {}
        for metadata in player_metadata_raw:

            if metadata.strip().startswith('Born'):
                player_metadata['birth'] = datetime.strptime(
                    metadata
                    .replace('Born:', '')
                    .strip(),
                    '%Y-%m-%d'
                ).date()

            if metadata.strip().startswith('Club'):
                player_metadata['current_club'] = (
                    metadata
                    .replace('Club:', '')
                    .strip()
                )

            if metadata.strip().startswith('Footed'):
                player_metadata['preferred_foot'] = (
                    metadata
                    .replace('Footed: ', '')
                )
            if metadata.strip().startswith('Height'):
                player_metadata['height_cm'] = (
                    metadata
                    .replace('Height: ', '')
                )

            if metadata.strip().startswith('National Team'):
                player_metadata['national_team'] = (
                    metadata
                    .replace('National Team:', '')
                    .strip()
                )

            if metadata.strip().startswith('Position'):
                player_metadata['position'] = (
                    metadata
                    .replace('Position: ', '')
                )

            if metadata.strip().startswith('Weight'):
                player_metadata['weight_kg'] = (
                    metadata
                    .replace('Weight: ', '')
                )


            for key in ['player_fullname',
                        'position',
                        'height_cm',
                        'weight_kg',
                        'preferred_foot',
                        'birth',
                        'nationality',
                        'national_team',
                        'current_club',
                        ]:
                if key not in player_metadata:
                    player_metadata[key] = ''

        for key in ['height_cm', 'weight_kg']:
            if player_metadata[key] == '':
                player_metadata[key] = 0

        if player_metadata['birth'] == '':
            player_metadata['birth'] = date(1, 1, 1)

        log.debug(player_metadata)
        log.info(f'Finished parsing metadata for {name}.')

        return PlayerMetadata(
            name=name,
            code=player_code,
            fullname=player_metadata['player_fullname'],
            height=player_metadata['height_cm'],
            weight=player_metadata['weight_kg'],
            nationality=player_metadata['nationality'],
            birthday=player_metadata['birth'],
            preferred_foot=player_metadata['preferred_foot'],
            position=player_metadata['position'],
            current_club=player_metadata['current_club'],
            national_team=player_metadata['national_team'],
        )

    def sink_metadata_to_db(self, player_code: str) -> None:
        with self.database.get_session() as session:
            stmt = select(DBPlayerMetadata).where(
                DBPlayerMetadata.code == player_code
            )

            player = session.execute(stmt).scalar()

            if player is None:
                player_metadata = self.get_player_metadata(player_code)

                log.info(f'Sinking metadata for {player_metadata.name}')

                session.add(
                    DBPlayerMetadata(
                        name=player_metadata.name,
                        code=player_metadata.code,
                        fullname=player_metadata.fullname,
                        height=player_metadata.height,
                        weight=player_metadata.weight,
                        nationality=player_metadata.nationality,
                        birthday=player_metadata.birthday,
                        preferred_foot=player_metadata.preferred_foot,
                        position=player_metadata.position,
                        current_club=player_metadata.current_club,
                        national_team=player_metadata.national_team,
                    )
                )

                session.commit()

                sleep(2)
            else:
                log.info(f'{player.name} already in database')


if __name__ == '__main__':
    pass
