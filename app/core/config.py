from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseModel):
    # 给定合理的默认值
    port: int = 8000
    version: str = "v1"
    log_level: str = "info"


class Settings(BaseSettings):
    # 实例化一个 BaseConfig 作为默认值，Pylance 就不会报错了
    base: BaseConfig = BaseConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


# 此时 Pylance 不会再报 "缺少参数" 的错误
settings = Settings()
