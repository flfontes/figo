
from sqlalchemy import select

from figo.etl.extraction.webscraper import Scraper
from figo.etl.loading.database import Database
from figo.etl.loading.models import DBPlayerLink
from figo.etl.transformation.players import AvailablePlayer, PlayerStatsList
from figo.settings.config import Settings


class ETL:
    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings
        self.database: Database = Database(self.settings.database)
        self.scraper: Scraper = Scraper()

    def get_links(self) -> None:
        AvailablePlayer(
            scraper=self.scraper,
            database=self.database,
            settings=self.settings,
        ).sink_to_db()

    def get_metadata(self, player_code: str) -> None:
        PlayerStatsList(
            database = self.database,
            settings = self.settings,
            scraper = self.scraper
        ).sink_metadata_to_db(player_code)

    def start_full_etl(self) -> None:
        self.database.create_db_and_tables()

        # self.get_links()

        with self.database.get_session() as session:
            stmt = select(DBPlayerLink.code)

            list_codes = session.execute(stmt).scalars()

            for code in list_codes:
                self.get_metadata(code)

        print('ETL Finished!')
