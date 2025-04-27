import os
from dotenv import load_dotenv

# Încărcăm variabilele din fișierul .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "./.env"))

class Settings:
    secret_key: str = os.getenv("SECRET_KEY", "")
    secret_key_refresh: str = os.getenv("SECRET_KEY_REFRESH", "")
    algorithm: str = os.getenv("ALGORITHM", "HS512")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    refresh_token_expire_minutes: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "60")
    )
    mongo: str = os.getenv("MONGO", "mongodb://localhost:27017")
    db_name: str = os.getenv("DB_NAME", "et_db")

    google_api: str = os.getenv("GOOGLE_API", "")
    foursquare: str = os.getenv("FOURSQUARE", "")

    google_autocomplete_url: str = os.getenv(
        "GOOGLE_AUTOCOMPLETE_URL", ""
    )
    google_places_details: str = os.getenv(
        "GOOGLE_PLACES_DETAILS", ""
    )
    google_places_nearby_search: str = os.getenv(
        "GOOGLE_PLACES_NEARBYSEARCH_URL", ""
    )
    google_places_text_search: str = os.getenv(
        "GOOGLE_PLACES_TEXTSEARCH_URL", ""
    )

settings = Settings()