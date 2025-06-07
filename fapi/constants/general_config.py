from fapi.fapi_config import settings


PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE":             0.00,  
    "PRICE_LEVEL_INEXPENSIVE":      0.25,  
    "PRICE_LEVEL_MODERATE":         0.50,  
    "PRICE_LEVEL_EXPENSIVE":        0.75,  
    "PRICE_LEVEL_VERY_EXPENSIVE":   1.00,  
}


NEARBY_SEARCH_URL=settings.google_places_nearby_search
TEXT_SEARCH_URL=settings.google_places_text_search
PLACE_DETAILS_URL=settings.google_places_details
GOOGLE_WEATHER_URL=settings.google_weather_api
PHOTO_ENDPOINT = "https://places.googleapis.com/v1/"