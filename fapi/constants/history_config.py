
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
    "reviews":("reviews",[])
    
}

EXTRA={
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
        "places.reviews"
        ]
}
CATEGORY_CONFIG = {
    "Muzee": {
        "nearby_type": ["museum"],
        "text_query": ["art museum", "history museum"],
        "excludedTypes": {"museum": []},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Galerii de arta": {
        "nearby_type": ["art_gallery"],
        "text_query": [],
        "excludedTypes": {"art_gallery":[]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Monumente": {
        "nearby_type": ["monument"],
        "text_query": [],
        "excludedTypes": {"monument": []},
        "textExcludedTypes": ["jewelry_store"],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Arhitectura": {
        "nearby_type": ["historical_place","landmark"],
        "text_query": ["historical places"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
}



