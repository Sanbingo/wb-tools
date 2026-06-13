from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "WB Financial Analyzer"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./wbtools.db"
    
    # WB API
    wb_api_token: str = ""
    
    # API Prefix
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
