


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
    "dinner":("servesDinner",""),
    "breakfast":("servesBreakfast",""),
    "lunch":("servesLunch",""),
    "reservable":("reservable",""),
    "groups":("goodForGroups",""),
    "vegan":("servesVegetarianFood",""),
    "outdoor":("outdoorSeating",""),
}

EXTRA={
   
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
        "places.goodForGroups",
        "places.servesDinner",
        "places.servesBreakfast",
        "places.servesBrunch",
        "places.servesLunch",
        "places.reservable",
        "places.servesVegetarianFood",
        "places.outdoorSeating",
        ]
}
CATEGORY_CONFIG = {
    "Asiatica": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["vietnamese_restaurant","chinese_restaurant","korean_restaurant"],
        "text_query": [],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "excludedTypes": {"vietnamese_restaurant":["pizza_restaurant","hamburger_restaurant"],"chinese_restaurant":["pizza_restaurant","hamburger_restaurant"],"korean_restaurant":["pizza_restaurant","hamburger_restaurant"]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Japoneza": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["ramen_restaurant","sushi_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Franceza": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["french_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Mexicana": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["mexican_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Tailandeza": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["thai_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
    "Indoneziana": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["indonesian_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Indiana": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["indian_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Mediteraneana": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["greek_restaurant","spanish_restaurant","acai_shop","seafood_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {"seafood_restaurant":["italian_restaurant"]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Africana": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["african_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Locala & Traditionala": {
        "nearby_type": [],
        "nearby_search_non_prim_types": [],
        "text_query": ["traditional local restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": ["restaurant"],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Turceasca": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["turskish_restaurant"],
        "text_query": ["kebab restaurant","shawarma restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Americana": {
        "nearby_type": ["american_restaurant"],
        "nearby_search_non_prim_types": ["american_restaurant","hamburger_restaurant","sandwich_shop"],
        "nearbyExcludedPrimaryTypes":["pizza_restaurant","meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {"american_restaurant":["chinese_restaurant"],"hamburger_restaurant":["chinese_restaurant"]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {
            "sandwich_shop":["american_restaurant","hamburger_restaurant"]
        },
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "din Orientul Mijlociu": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["lebanese_restaurant","afghani_restaurant","middle_eastern_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {"middle_eastern_restaurant":["turkish_restaurant"]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

    "Italiana": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["italian_restaurant","sandwich_shop","seafood_restaurant","pizza_restaurant"],
        "nearbyExcludedPrimaryTypes":["meal_delivery","catering_service"],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {"seafood_restaurant":["italian_restaurant"],"sandwich_shop":["italian_restaurant"],"pizza_restaurant":["italian_restaurant"]},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
   
    "default": {
        "nearby_type": ["restaurant"],
        "nearby_search_non_prim_types": ["restaurant"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
    
}
