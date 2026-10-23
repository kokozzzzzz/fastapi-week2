
from pydantic_settings import BaseSettings,SettingsConfigDict

# env中的配置获取
class Settings(BaseSettings):
    app_name: str = "FastAPI Week 2"
    debug: bool = True
    database_url : str = ""
    test_database_url: str = ""  # 测试数据库

    github_token : str = ""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        #extra="ignore",
    )


setting = Settings()




