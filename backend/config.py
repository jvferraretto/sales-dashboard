from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/sales.db"
    MELI_APP_ID: str = ""
    MELI_SECRET_KEY: str = ""
    MELI_REDIRECT_URI: str = "http://localhost:8000/auth/mercadolivre/callback"
    SHOPEE_PARTNER_ID: str = ""
    SHOPEE_PARTNER_KEY: str = ""
    SHOPEE_REDIRECT_URI: str = "http://localhost:8000/auth/shopee/callback"

    class Config:
        env_file = ".env"


settings = Settings()
