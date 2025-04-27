from fapi.fapi_config import settings
#urls
NEARBY_SEARCH_URL=settings.google_places_nearby_search
TEXT_SEARCH_URL=settings.google_places_text_search
PLACE_DETAILS_URL=settings.google_places_details
#FOR price score
PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE":             0.00,  # 0
    "PRICE_LEVEL_INEXPENSIVE":      0.25,  # 1
    "PRICE_LEVEL_MODERATE":         0.50,  # 2
    "PRICE_LEVEL_EXPENSIVE":        0.75,  # 3
    "PRICE_LEVEL_VERY_EXPENSIVE":   1.00,  # 4
}

SHOPPING_EXTRA={
    "keywords":["Mall", "Shopping Centre", "Commercial Centre", "complex"],
    "Mask":["places.displayName",
        "places.primaryType",
        "places.types",
        "places.containingPlaces",
        "places.rating",
        "places.userRatingCount",
        "places.priceLevel",
        "places.photos",
        "places.location",
        "places.regularOpeningHours",
        "places.placeId"
        ]
}
SHOPPING_CATEGORY_CONFIG = {
    "Librarii": {
        "nearby_type": ["book_store"],
        "text_query": ["book store", "vintage book store"],
        "excludedTypes": [],
        "textExcludedTypes": []
    },
    "Souveniruri & Cadouri": {
        "nearby_type": [],
        "text_query": ["souvenir shop", "souvenir store"],
        "excludedTypes": [],
        "textExcludedTypes": []
    },
    "Bijuterii": {
        "nearby_type": ["jewelry_store"],
        "text_query": ["jewelry store"],
        "excludedTypes": [],
        "textExcludedTypes": []
    },
    "Moda si accesorii": {
        "nearby_type": ["clothing_store", "shoe_store"],
        "text_query": ["clothing store", "fashion accessories", "footwear store"],
        "excludedTypes": [],
        "textExcludedTypes": []
    },
    "Cosmetice si parfumuri": {
        "nearby_type": [],
        "text_query": ["cosmetics store", "perfume store"],
        "excludedTypes": [],
        "textExcludedTypes": []
    },
    "Antichitati": {
        "nearby_type": [],
        "text_query": ["antique store"],
        "excludedTypes": [],
        "textExcludedTypes": []
    },
    "Produse locale": {
        "nearby_type": [],
        "text_query": ["traditional store", "traditional food store"],
        "excludedTypes": [],
        "textExcludedTypes": []
    },
}

