import os
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config.db_config import DatabaseConfig
from src.model.conector import DatabaseConectorPostgres

from src.config.settings import env


# Configuracion de la BAs de datos
db_config = DatabaseConfig(
    nameDatabase=env.postgres_db_name,
    user=env.postgres_user,
    password=env.postgres_password,
    host=env.postgres_host,
    port=env.postgres_port
)

# Conexion de la base de datos d ePOasgres
db_conector = DatabaseConectorPostgres(db_config)
engine = db_conector.create_engine()

# Crear session
session = sessionmaker(bind=engine)

# Crear base para crear tablas
Base = declarative_base()
