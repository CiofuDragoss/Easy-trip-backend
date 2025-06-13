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
    "reviews":("reviews",[]),
    "liveMusic":("liveMusic",""),
    "sports":("goodForWatchingSports","")
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
        "places.reviews",
        "places.liveMusic",
        "places.goodForWatchingSports"
        ]
}

CATEGORY_CONFIG={

    "Pub": {
        "nearby_type": ["pub"],
        "nearby_search_non_prim_types": ["pub"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": ["night pub"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": ["pub","bar"],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Karaoke": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["karaoke"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": ["karaoke club"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {"karaoke":["bar","night_club"]},
        "textIncludedTypes": ["karaoke","bar"],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Lounge": {
        "nearby_type": ["night_club","bar"],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": ["lounge"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Bar de noapte": {
        "nearby_type": ["night_club","bar"],
        "nearby_search_non_prim_types": ["bar"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": ["night bar"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {"night_club":["bar"]},
        "textIncludedTypes": ["bar","night_club"],
        "bannedWordsNearby": ["gentlemen","strip"],
        "bannedWordsText": ["gentlemen","strip"]
    },
    "Club de Noapte": {
        "nearby_type": ["night_club"],
        "nearby_search_non_prim_types": ["night_club"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": ["night club"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": ["night_club","bar"],
        "bannedWordsNearby": ["gentlemen","strip"],
        "bannedWordsText": ["gentlemen","strip"]
    },
}