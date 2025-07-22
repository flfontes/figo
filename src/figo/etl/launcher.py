from figo.etl.extraction.webscraper import Scraper
from figo.etl.loading.database import Database
from figo.settings.config import Settings


class ETL:
    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings
        self.database: Database = Database(self.settings.database)
        self.scraper: Scraper = Scraper()

    def start_full_etl(self) -> None:
        pass
