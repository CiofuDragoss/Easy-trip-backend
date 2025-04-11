from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS512"
    access_token_expire_minutes: int = 30
    mongo: str = "mongodb://localhost:27017"
    db_name:str="et_db"
    google_api:str
    foursquare:str
    google_autocomplete_url:str
    google_places_details: str 
    class Config:
        env_file = "fapi/.env"

settings = Settings()