


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
    "beer":("servesBeer",""),
    "wine":("serversWine",""),
    "coffee":("servesCoffee",""),
    "cocktail":("servesCocktails",""),
    "dessert":("servesDessert",""),
    "group":("goodForGroups",""),
    "vegan":("servesVegetarianFood",""),
    "outdoor":("outdoorSeating",""),
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
        "places.goodForGroups",
        "places.servesDessert",
        "places.servesCocktails",
        "places.servesWine",
        "places.servesCoffee",
        "places.servesVegetarianFood",
        "places.servesBeer",
        "places.outdoorSeating"
        
        ]
}
CATEGORY_CONFIG = {
    
    "Cafenea": {
        "nearby_type": ["cafe"],
        "nearby_search_non_prim_types": ["cafe","coffe_shop"],
        "nearbyExcludedPrimaryTypes":["supermarket"],
        "text_query": [],
        "excludedTypes": {"cafe":["playground","fast_food_restaurant"],"coffe_shop":["playground","fast_food_restaurant"]},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Bar": {
        "nearby_type": ["bar"],
        "nearby_search_non_prim_types": ["bar"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": [],
        "excludedTypes": {"bar":['barbecue_area','hotel','playground']},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    "Pub": {
        "nearby_type": ["pub"],
        "nearby_search_non_prim_types": ["pub"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

     "Ceainarie": {
        "nearby_type": ["tea_house"],
        "nearby_search_non_prim_types": [],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": ["tea house"],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": ["tea_house"],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

    "Vinarie": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["wine_bar"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": [],
        "excludedTypes": {"wine_bar":['clothing_store','event_venue']},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

    
    "Cofetarie & Dulciuri": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["confectionery","dessert_restaurant","donut_shop","candy_store"],
        "nearbyExcludedPrimaryTypes":["italian_restaurant","pizza_restaurant"],
        "text_query": [],
        "excludedTypes": {
            "confectionery": ["fast_food_restaurant", "hamburger_restaurant"],
            "dessert_restaurant": ["fast_food_restaurant", "hamburger_restaurant"],
            "donut_shop": ["fast_food_restaurant", "hamburger_restaurant"],
            "candy_store": ["fast_food_restaurant", "hamburger_restaurant"]
        },
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

    "Bar de sucuri fresh": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["juice_shop"],
        "nearbyExcludedPrimaryTypes":[],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

    "Gelaterie": {
        "nearby_type": [],
        "nearby_search_non_prim_types": ["ice_cream_shop"],
        "nearbyExcludedPrimaryTypes":["pizza_shop","food_delivery","fast_food_restaurant"],
        "text_query": [],
        "excludedTypes": {"ice_cream_shop":{"food_delivery"}},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": {},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },

    
    
    
}