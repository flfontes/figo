import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DBPlayerLink(Base):
    __tablename__ = 'player_links'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    code: Mapped[str]
    link: Mapped[str]


class DBPlayerStats(Base):
    __tablename__ = 'player_stats'

    id: Mapped[int] = mapped_column(primary_key=True)


class DBPlayerMetadata(Base):
    __tablename__ = 'player_metadata'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    code: Mapped[str]
    fullname: Mapped[str]
    height: Mapped[int]
    weight: Mapped[int]
    nationality: Mapped[str]
    birthday: Mapped[datetime.date]
    preferred_foot: Mapped[str]
    position: Mapped[str]
    current_club: Mapped[str]
    national_team: Mapped[str]
