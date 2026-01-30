from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "coffee-shop"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/coffeeshop"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_queue: str = "orders"

    model_config = SettingsConfigDict(env_prefix="COFFEE_", env_file=".env")


settings = Settings()
