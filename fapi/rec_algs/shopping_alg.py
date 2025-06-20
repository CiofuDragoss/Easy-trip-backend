from fapi.helpers.math_helpers import wilson_score,gauss_score,haversine_distance
import asyncio

from fapi.constants.shopping_config import CATEGORY_CONFIG,EXTRA,ENRICHED
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center
from fapi.routes.google_routes import safe_google_details,google_nearby_search,google_text_search
from pprint import pprint
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos
import math
from functools import partial

        
        
    









async def shopping_alg(main_questions,shopping_questions,max_places=12,min_places=8):

    loop = asyncio.get_running_loop()
    distance=int(main_questions.distance*1000)
    budget= main_questions.budget
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    cat=shopping_questions.shoppingExperience
    local=shopping_questions.shoppingLocType
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
    helpers_score=[partial(rating_score,condition=3.6,z=1.4),
                   partial(dist,userLat=latitude,userLong=longitude,condition=2800,radius=distance,ratio=1.5),
                   partial(price_score,budget=budget,sigma=0.45),
                   partial(local_score,local=local,sigma=0.4),
                   ]
    
    ratios=[0.45,0.2,0.1,0.25]
    criteria_classification=["+","-","+","+"]
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
            needs_normalization,
            0.5,
            max_places,
            min_places
            
        )
        cleaned_data[shopping_type]=loc_score_results
    
    
    
    yield {
        "stage": "final",
        "data": cleaned_data
    }

async def getMallScore(place,keywords):
    display=place["display"]
    highlight=None
    inMall=1 if any(kw.lower() in display.lower() for kw in keywords) else 0
    
    if inMall==0 and place.get("containingPlaces"):
        tasks=[safe_google_details(p["id"]) for p in place["containingPlaces"]]
        for detail in await asyncio.gather(*tasks):
            if "shopping_mall" in detail.get("types",[]):
                inMall=1
                print("avem in mallll")
                break
    highlight="Locatia se afla intr un mall." if inMall==1 else "Locatia este stradala."
    return "inMall",inMall,highlight




def local_score(place,local,condition=None,sigma=0.4):
    highlight=None
    inMall=place.get("inMall")
    localScore=gauss_score(inMall,local,sigma=sigma)
    return "localScore",round(localScore,5),highlight

