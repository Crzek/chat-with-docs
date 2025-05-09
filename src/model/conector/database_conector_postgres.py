"""configuration Database Conector Postgres
"""

from sqlalchemy import create_engine
from src.config.db_config import DatabaseConfig


class DatabaseConectorPostgres:

    def __init__(self, dbconfig: DatabaseConfig) -> None:
        """Constructor

        Args:
            dbconfig (DatabaseConfig): Base DataBAse Config
            full_url (str): Full URL for connection
            engine (object): Engine for connection
        """
        self.dbconfig = dbconfig
        self.full_url = f"postgresql://{self.dbconfig.user}:{self.dbconfig.password}" \
            f"@{self.dbconfig.host}:{self.dbconfig.port}" \
            f"/{self.dbconfig.nameDatabase}"
        # # otra forma de hacerlo
        # self.full_url = (
        #     f"postgresql://{self.dbconfig.user}:{self.dbconfig.password}"
        #     f"@{self.dbconfig.host}:{self.dbconfig.port}"
        #     f"/{self.dbconfig.nameDatabase}"
        # )
        self.engine = self.create_engine()

    def create_engine(self):
        return create_engine(self.full_url)
