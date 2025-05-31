from fapi.helpers.math_helpers import wilson_score,gauss_score,haversine_distance
import asyncio

from fapi.constants.shopping_config import PRICE_LEVEL_MAP,CATEGORY_CONFIG,EXTRA,ENRICHED
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center
from fapi.routes.google_routes import safe_google_details,google_nearby_search,google_text_search
from pprint import pprint
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score
import math
from functools import partial
from time import perf_counter
        
        
    









async def shopping_alg(main_questions,shopping_questions):

    loop = asyncio.get_running_loop()
    distance=main_questions.distance*1000
    budget= main_questions.budget
    local=shopping_questions.shoppingLocType
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    cat=shopping_questions.shoppingExperience
    
    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=distance
    )
    loc_restr = LocationRestriction(circle=circle)
    shoppingTypes = [
        {
      "key": key.strip(),
      **CATEGORY_CONFIG[key.strip()]
    }
        for key in cat
    ]

    
    
    helpers_enrich=[partial(getMallScore,keywords=EXTRA.get("mall")),
                    solve_photos]
    helpers_score=[partial(rating_count,condition=3.6,z=1.4),
                   partial(distance,userLat=latitude,userLong=longitude,condition=2800,radius=distance,ratio=1.5),
                   partial(price_score,budget=budget,sigma=0.45),
                   partial(local_score,local=local,sigma=0.4),
                   ]
    
    ratios=[0.45,0.2,0.1,0.25]
    needs_classification=[False,True,False,False]
    needs_normalization=[False,True,False,False]
    yield {
        "stage": "pas 1",
        "info": "Cautam locatii din zona in care te afli..."
    }
    raw_data=await fetch_places(shoppingTypes,loc_restr,EXTRA)
    yield{
        "stage": "pas 2",
        "info": "pregatim locatiile si le filtram..."
    }
    cleaned_data=await enrich_all(raw_data,ENRICHED,helpers_enrich,CATEGORY_CONFIG)
    
    for shopping_type,places in cleaned_data.items():
        loc_score_results = await loop.run_in_executor(
            DEFAULT_THREAD_POOL,
            compute_score,
            places,
            helpers_score,
            ratios,
            criteria_classification,
            needs_normalization
            
        )
        cleaned_data[shopping_type]=loc_score_results
    
    
    
    yield {
        "stage": "final",
        "data": cleaned_data
    }

async def getMallScore(place,keywords):
    display=place["displayName"]["text"]
    highlight=None
    inMall=1 if any(kw.lower() in display.lower() for kw in keywords) else 0
    
    if inMall==0 and place.get("containingPlaces"):
        tasks=[safe_google_details(p["id"]) for p in place["containingPlaces"]]
        for detail in await asyncio.gather(*tasks):
            if "shopping_mall" in detail.get("types",[]):
                inMall=1
                break
    highlight="Locatia se afla intr un mall." if inMall==1 else "Locatia este stradala."
    return "inMall",inMall,highlight

def solve_photos(place):
    photos=place.get("photos","")
    highlight=None
    if photos:
        photos=photos[:4]
        photo_names=[photo.get("name") for photo in photos if photo.get("name")]
        return "photos",photo_names,highlight
    raise Exception()

def rating_count(place,condition=None,z=1.4):
    highlight=None
    rating=place.get("rating")
    if condition and rating<condition:
         raise Exception()
    ratingCount=place.get("ratingCount")
    ratingScore=wilson_score(rating,ratingCount,z)
    if ratingScore>0.85:
        highlight="Locatia aceasta are ratinguri excelente."
    return "ratingScore",round(ratingScore,5),highlight

def distance(place,userLat,userLong,radius,condition=None,ratio=1.5):
    highlight=None
    sigma=radius/ratio
    latitude=place.get("latitude")
    longitude=place.get("longitude")
    dist=haversine_distance(latitude,longitude,userLat,userLong)
    if dist<1300:

        highlight="Locatia este foarte aproape de tine!"
    if condition and (dist-radius)>condition:
         raise Exception()

    return "distance",dist,highlight

def price_score(place,budget,condition=None,sigma=0.45):
    priceScore=1
    highlight=None
    priceLevel=place.get("priceLevel")
    if priceLevel:
        price_level_value=PRICE_LEVEL_MAP[priceLevel]
        priceScore=gauss_score(price_level_value,budget,sigma=sigma)
    return "priceScore",round(priceScore,5),highlight

def local_score(place,local,condition=None,sigma=0.4):
    highlight=None
    inMall=place.get("inMall")
    localScore=gauss_score(inMall,local,sigma=sigma)
    return "localScore",round(localScore,5),highlight

