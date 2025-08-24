from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    database: str = ''
    base_url: str = ''
    players_url: str = ''
    competitions_url: str = ''
    domestic_league_code: str = ''
    domestic_league_long: str = ''
    domestic_cup_code: str = ''
    domestic_cup_long: str = ''
    international_cup_code: str = ''
    international_cup_long: str = ''
    national_team_code: str = ''
    national_team_long: str = ''
