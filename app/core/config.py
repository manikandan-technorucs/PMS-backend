from typing import Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TechnoRUCS PMS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    MYSQL_USER: str = Field(alias="DB_USER")
    MYSQL_PASSWORD: str = Field(alias="DB_PASSWORD")
    MYSQL_SERVER: str = Field(alias="DB_SERVER", default="localhost")
    MYSQL_PORT: str = Field(alias="DB_PORT", default="3306")
    MYSQL_DB: str = Field(alias="DB_NAME")
    
    @property
    def DATABASE_URL(self) -> str:
        import urllib.parse
        encoded_password = urllib.parse.quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+pymysql://{self.MYSQL_USER}:{encoded_password}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
    
    SECRET_KEY: str = Field(default="supersecretkey_please_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  

    # CORS
    BACKEND_CORS_ORIGINS: Union[list[str], str] = Field(default=[])

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            return json.loads(v)
        elif isinstance(v, list):
            return v
        return v

    # Async configuration (Redis + Celery)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Email logic
    EMAIL_PROVIDER: str = Field(default="sendgrid")
    SENDGRID_API_KEY: str = Field(default="")
    
    # SMTP logic (for Outlook/Gmail)
    SMTP_HOST: str = Field(default="smtp-mail.outlook.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    EMAIL_FROM: str = Field(default="noreply@technorucs.com")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
