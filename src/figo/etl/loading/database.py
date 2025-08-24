from pydantic import BaseModel
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from figo.etl.loading.models import Base


class Database:
    def __init__(self, db: str) -> None:
        self.engine: Engine = create_engine(db)

    def get_session(self) -> Session:
        return Session(self.engine)

    def create_db_and_tables(self) -> None:
        Base().metadata.create_all(self.engine)

    def add_to_database(self, table_name: str, row_object: BaseModel) -> None:
        with self.get_session() as session:
            pass

    def check_if_exists(self) -> None:
        pass
