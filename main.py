from figo.etl.launcher import ETL
from figo.settings.config import Settings


settings = Settings()

etl = ETL(settings)

etl.start_full_etl()
# etl.get_metadata('9c60f681')
# etl.get_metadata('dea698d9')
