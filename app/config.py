from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    model_config = SettingsConfigDict(env_file= ".env", extra= "ignore")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"ENV_STATE from BaseConfig: {self.ENV_STATE}")

class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLLBACK: bool = False
    LOGTAIL_API_KEY: Optional[str] = None
    

class DevConfig(GlobalConfig):
    DATABASE_URL: Optional[str] = None
    model_config = SettingsConfigDict(env_prefix= "DEV_")
        

class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix= "PROD_")

class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLLBACK: bool = True
    model_config = SettingsConfigDict(env_prefix= "TEST_")

@lru_cache()
def getConfig(env_state: str):
    configs = { "dev": DevConfig, "prod": ProdConfig, "test": TestConfig }
    if env_state is None:
        raise ValueError("ENV_STATE is not set")
    return configs[env_state]()

config = getConfig(BaseConfig().ENV_STATE)