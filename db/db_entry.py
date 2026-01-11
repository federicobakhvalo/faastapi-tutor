
from config.db_config import DBSettings
from db.api import Database

settings = DBSettings()
db: Database = Database(url=settings.url, echo=settings.echo)
