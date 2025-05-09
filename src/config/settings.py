from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # permite variables no definidas
    )
    pdf_path: str = Field(default="rag/consultorio.pdf")
    db_path: str = Field(default="chromadb.db")
    openai_model: str = Field(default="gpt-4.1-nano")
    anthropic_model: str = Field(default="claude-1")
    embedding_model: str = Field(default="text-embedding-ada-002")

    # APIS
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(env="ANTHROPIC_API_KEY")

    # APP config
    app_host: str
    app_port: int

    upload_dir: str

    # Base de datos
    postgres_db_name: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int


# Instancia única


env = Settings()
