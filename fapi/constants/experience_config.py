


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

EXTRA = {
    "type_config": {
        "park": {
            "indoor": 0,
            "physical": 0.3,
            "adrenaline": 0
        },
        "movie_theater": {
            "indoor": 1,
            "physical": 0,
            "adrenaline": 0
        },
        "marina": {
            "indoor": 0,
            "physical": 1,
            "adrenaline": 0,
            "needs_wheater":0
        },
        "hiking_area": {
            "indoor": 0,
            "physical": 1,
            "adrenaline": 0.35
        },
        "botanical_garden": {
            "indoor": 0.1,
            "physical": 0.2,
            "adrenaline": 0
        },
        "tour_agency": {
            "indoor": 1,
            "physical": 0,
            "adrenaline": 0
        },
        "wellness_center": {
            "indoor": 1,
            "physical": 0.1,
            "adrenaline": 0
        },
        "swimming_pool": {
            "indoor": 0.2,
            "physical": 0.6,
            "adrenaline": 0
        },
        "ski_resort": {
            "indoor": 0,
            "physical": 1,
            "adrenaline": 1,
            "needs_wheater":0,
        },
        "plaza": {
            "indoor": 0,
            "physical": 0.2,
            "adrenaline": 0
        },
        "karaoke": {
            "indoor": 1,
            "physical": 0,
            "adrenaline": 0
        },
        "comedy_club":
        {
            "indoor": 1,
            "physical": 0.1,
            "adrenaline": 0,
            
        },
        "bowling_alley":{
            "indoor": 1,
            "physical": 0.1,
            "adrenaline": 0.1,
        },

        "beach": {
            "indoor": 0,
            "physical": 0.6,
            "adrenaline": 0.1,
            "needs_wheater":1,
        },
        "zoo": {
            "indoor": 0,
            "physical": 0,
            "adrenaline": 0.1
        },
        "water_park": {
            "indoor": 0,
            "physical": 0.4,
            "adrenaline": 0.6,
            "needs_wheater":1,
        },
        "roller_coaster": {
            "indoor": 0,
            "physical": 0,
            "adrenaline": 0.8
        },
        "amusement_park": {
            "indoor": 0,
            "physical": 0.2,
            "adrenaline": 0.6
        },
        "ferris_wheel": {
            "indoor": 0,
            "physical": 0,
            "adrenaline": 0.6
        },
        "adventure_sports_center": {
            "indoor": 0,
            "physical": 1,
            "adrenaline": 0.7,
            "needs_wheater":1,
        }
    },
    "Mask": [
        "places.displayName",
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
    "Experiente": {
        "nearby_type": [],
        "nearby_search_non_prim_types": [
            "park",
            "movie_theater",
            "marina",
            "hiking_area",
            "botanical_garden",
            "tour_agency",
            "bowling_alley",
            "comedy_club",

            "wellness_center",
            "swimming_pool",
            "ski_resort",
            "plaza",
            "karaoke",
            "beach",
            "zoo",
            "water_park",
            "roller_coaster",
            "amusement_park",
            "ferris_wheel",
            "adventure_sports_center"
        ],
        "text_query": [],
        "excludedTypes": {},
        "textExcludedTypes": [],
        "nearbyIncludedTypes": [],
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
    
}
