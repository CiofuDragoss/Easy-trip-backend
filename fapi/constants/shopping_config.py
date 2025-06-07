
#urls

#FOR price score
PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE":             0.00,  # 0
    "PRICE_LEVEL_INEXPENSIVE":      0.25,  # 1
    "PRICE_LEVEL_MODERATE":         0.50,  # 2
    "PRICE_LEVEL_EXPENSIVE":        0.75,  # 3
    "PRICE_LEVEL_VERY_EXPENSIVE":   1.00,  # 4
}


ENRICHED={
    "display":       ("displayName.text",   ""),
    "primaryType":   ("primaryType",        ""),
    "types":         ("types",              []),
    "rating":        ("rating",             0),
    "placeId":       ("id",                 ""),
    "ratingCount":   ("userRatingCount",    0),
    "priceLevel":    ("priceLevel",         ""),
    "latitude":      ("location.latitude",  None),
    "longitude":     ("location.longitude", None),
    "photos":       ("photos",             []),
    "openingHours":  ("regularOpeningHours", []),
    "reviews":("reviews",[]),
    
    
}

EXTRA={
    "mall":["Mall", "Shopping Center", "Commercial Center", "complex"],
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
        "places.id",
        "places.reviews",
        
        
        ]
}
CATEGORY_CONFIG = {
    "Librarii": {
        "nearby_type": ["book_store"],
        "text_query": ["book store", "vintage book store"],
        "excludedTypes": {"book_store": []},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Souveniruri & Cadouri": {
        "nearby_type": ["gift_shop"],
        "text_query": ["souvenirs", "traditional gifts"],
        "excludedTypes": {},
        "textExcludedTypes": ["supermarket"],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": ["online","print"],
        "bannedWordsText": ["online","print"]
    },
    "Bijuterii": {
        "nearby_type": ["jewelry_store"],
        "text_query": ["jewelry store"],
        "excludedTypes": {"jewelry_store": []},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Moda si accesorii": {
        "nearby_type": ["clothing_store", "shoe_store"],
        "text_query": ["clothing store", "fashion accessories", "footwear store"],
        "excludedTypes": {"clothing_store": [], "shoe_store": []},
        "textExcludedTypes": ["jewelry_store"],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Cosmetice si parfumuri": {
        "nearby_type": [],
        "text_query": ["cosmetics store", "perfume store"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Antichitati": {
        "nearby_type": [],
        "text_query": ["antique store"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [
            "art_gallery",
            "jewelry_store",
            "home_goods_store",
            "furniture_store",
            "book_store",
            "discount_store",
            "home_improvement_store"
        ],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Produse locale": {
        "nearby_type": [],
        "text_query": ["traditional store", "traditional food store"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Alte locuri interesante": {
        "nearby_type": ["shopping_mall"],
        "text_query": ["local market"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    }
}



