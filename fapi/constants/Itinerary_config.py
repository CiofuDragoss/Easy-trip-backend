ENRICHED_RELAX={
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

EXTRA_RELAX={
   
    "Mask":["places.displayName",
        "places.primaryType",
        "places.types",
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

CATEGORY_CONFIG_RELAX = {
    "Cafenea": {
        "nearby_type": ["coffee_shop","cafe"],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes": [],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Bar": {
        "nearby_type": ["bar"],
        "nearby_search_non_prim_types": ["bar"],
        "nearbyExcludedPrimaryTypes": [],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Pub": {
        "nearby_type": ["pub"],
        "nearby_search_non_prim_types": ["pub"],
        "text_query": [],
        "excludedTypes": {},
        "nearbyExcludedPrimaryTypes": [],
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Gustare dulce": {
        "nearby_type": ["dessert_shop","confectionery","donut_shop"],
        "nearby_search_non_prim_types": ["dessert_restaurant"],
        "nearbyExcludedPrimaryTypes": [],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Gustare": {
        "nearby_type": ["bagel_shop", "acai_shop", "bakery","deli","fast_food_restaurant","sandwich_shop" ],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes": [],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Inghetata": {
        "nearby_type": ["ice_cream_shop"],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes": [],
        "text_query": ["ice cream place"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Parc": {
        "nearby_type": ["park"],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes": [],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

    "default":{
        "nearby_type": ["park","cafe","sandwich_shop","donut_shop","confectionery","ice_cream_shop","bar"],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes": [],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
}
