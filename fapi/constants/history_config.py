


ENRICHED={
    "display":       ("displayName.text",   ""),
    "displayStruct":       ("displayName",   ""),
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
    "QUERY_SCORE_MAP":{
        "art museum":0.9,
        "history museum":0.2,
        "art_gallery":1,
        "monument":0.3,
        "historical_place":0.2,
        "landmark":0.2,
        "historical places":0.3,
        "art_studio":1,
        "sculpture":0.5,
        "art expo":1,
        "art gallery":1,
        "museum":0.5,


    },
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
        "text_query": ["art museum","history museum"],
        "excludedTypes": {"museum": []},
        "textExcludedTypes": ["library"],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Galerii de arta": {
        "nearby_type": ["art_gallery","art_studio"],
        "text_query": ["art gallery","art expo"],
        "excludedTypes": {"art_gallery":[]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Monumente": {
        "nearby_type": ["monument","sculpture"],
        "text_query": [],
        "excludedTypes": {"monument": []},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Arhitectura": {
        "nearby_type": ["historical_place","cultural_landmark"],
        "text_query": ["historical places"],
        "excludedTypes": {"historical_place":[],"landmark":[]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
}



