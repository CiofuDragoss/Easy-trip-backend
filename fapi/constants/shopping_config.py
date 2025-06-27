
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
    "containingPlaces": ("containingPlaces", []),
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
        "places.priceRange",
        
        
        ]
}
CATEGORY_CONFIG = {
    "Librarii": {
        "nearby_type": ["book_store"],
        "nearby_search_non_prim_types": [],
        "text_query": ["book store", "vintage book store"],
        "excludedTypes": {"book_store": []},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Souveniruri & Cadouri": {
        "nearby_type": [],
        "nearby_search_non_prim_types": [],
        "text_query": ["souvenirs", "local gifts","traditional gifts"],
        "excludedTypes": {"gift_shop": []},
        "textExcludedTypes": ["supermarket"],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": ["online", "print"],
        "bannedWordsText": ["online", "print"]
    },
    "Bijuterii": {
        "nearby_type": ["jewelry_store"],
        "nearby_search_non_prim_types": ["jewelry_store"],
        "nearbyExcludedPrimaryTypes":["finance"],
        "text_query": [],
        "excludedTypes": {"jewelry_store": []},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Moda si accesorii": {
        "nearby_type": ["clothing_store", "shoe_store"],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": ["fashion accessories"],
        "excludedTypes": {"clothing_store": ["child_care_agency","tailor","gift_shop","wedding_venue"], "shoe_store": ["child_care_agency","tailor","gift_shop","wedding_venue"]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": ["clothing_store"],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Cosmetice si parfumuri": {
        "nearby_type": [],
        "nearby_search_non_prim_types": [],
        "text_query": ["cosmetics store", "perfume store"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Antichitati": {
        "nearby_type": [],
        "nearby_search_non_prim_types": [],
        "text_query": ["antique store"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [
            "art_gallery", "jewelry_store", "home_goods_store",
            "furniture_store", "book_store", "discount_store",
            "home_improvement_store"
        ],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Produse locale": {
        "nearby_type": [],
        "nearby_search_non_prim_types": [],
        "text_query": ["traditional store","traditional shop"],
        "excludedTypes": {},
        "textExcludedTypes": ["fast_food_restaurant","pub","bar","restaurant"],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
    
    "default": {
        "nearby_type": ["shopping_mall"],
        "nearby_search_non_prim_types": [],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    }
}



