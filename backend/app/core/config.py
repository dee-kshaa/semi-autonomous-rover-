from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    ENVIRONMENT: str = 'development'
    PROJECT_NAME: str = 'Mobile Network Intelligence API'
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str = 'change-this-secret-key'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'network_intelligence'

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )

    @model_validator(mode='after')
    def validate_secret_key(self):
        if self.ENVIRONMENT.lower() == 'production' and self.SECRET_KEY == 'change-this-secret-key':
            raise ValueError('SECRET_KEY must be set via environment variables in production')
        return self


settings = Settings()
