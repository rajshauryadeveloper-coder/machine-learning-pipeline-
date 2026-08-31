from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "Machine Learning Pipeline"
    debug: bool = False

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "ecommerce_database"
    db_user: str = "shaurya"
    db_password: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
