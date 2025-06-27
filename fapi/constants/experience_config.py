


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
    "physical": 0.2,
    "duration":75,
    
  },
  "movie_theater": {
    "indoor": 1,
    "physical": 0,
    "duration":120,
  },
  "aquarium": {
    "indoor": 1,
    "physical": 0,
    "duration":45,
  },
  "hiking_area": {
    "indoor": 0,
    "physical": 1,
    "needs_weather": 1,
    "duration":180,
  },
  "botanical_garden": {
    "indoor": 0,
    "physical": 0.2,
    "duration":60,
  },
  "bowling_alley": {
    "indoor": 1,
    "physical": 0.2,
    "duration":95,
  },
  "swimming_pool": {
    "indoor": 0.5,
    "physical": 0.6,
    "needs_weather": 1,
    "duration":150,
  },
  "ski_resort": {
    "indoor": 0,
    "physical": 1,
    "needs_weather": 0,
    "duration":180,
  },
  "beach": {
    "indoor": 0,
    "physical": 0.3,
    "needs_weather": 1,
    "duration":155,
  },
  "zoo": {
    "indoor": 0.2,
    "physical": 0.1,
    "duration":95,
  },
  "tourist_attraction": {
    "indoor": 0.5,
    "physical": 0.3,
    "duration":45,
  },
  "water_park": {
    "indoor": 0,
    "physical": 0.7,
    "needs_weather": 1,
    "duration":150,
  },
  "ferris_wheel": {
    "indoor": 0,
    "physical": 0,
    "duration":30,
  },
  "adventure_sports_center": {
    "indoor": 0,
    "physical": 1,
    "needs_weather": 1,
    "duration":120,
  },
  "observation_deck":{
    "indoor": 0,
    "physical": 0.2,
    "duration":45,
  },
  "planetarium":{
    "indoor": 1,
    "physical": 0,
    "duration":55,
  },
  "comedy_club":{
    "indoor": 1,
    "physical": 0,
    "duration":55,
  },
  "circus":{
    "indoor": 1,
    "physical": 0,
    "duration":90,
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
        "nearby_type": ["swimming_pool","tourist_attraction"],
        "nearby_search_non_prim_types": [
            "park",
            "movie_theater",
            "aquarium",
            "hiking_area",
            "botanical_garden", 
            "bowling_alley",
            "ski_resort",
            "comedy_club",
            "planetarium",
            "beach",
            "zoo",
            "water_park",
            "ferris_wheel",
            "adventure_sports_center",
            "observation_deck"
        ],
        "text_query": ["circus"],
        "excludedTypes": {"swimming_pool":["sports_activity_location"],'tourist_attraction':["casino","restaurant","monument","sculpture"],"park":["playground","dog_park"],"zoo":['amusement_center','amusement_park'],"observation_deck":["food_delivery","general_contractor"],"adventure_sports_center":{'tour_agency', 'travel_agency','real_estate_agency','childrens_camp','school', 'summer_camp_organizer'},"hiking_area":{'tour_agency', 'travel_agency','real_estate_agency','childrens_camp','school', 'summer_camp_organizer'}},
        "textExcludedTypes": ["sports_club","child_care_agency","school","restaurant"],
        "nearbyIncludedTypes": {"park":['tourist_attraction']},
        "textIncludedTypes": [],
        "bannedWordsNearby": [],
        "bannedWordsText": []
    },
    
    
}
