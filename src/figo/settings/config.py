from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    database: str = ''
    base_url: str = ''
    players_url: str = ''
    competitions_url: str = ''
