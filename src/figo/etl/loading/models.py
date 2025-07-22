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
