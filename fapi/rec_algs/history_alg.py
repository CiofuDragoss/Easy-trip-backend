import asyncio
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center
from fapi.constants.history_config import CATEGORY_CONFIG,EXTRA,ENRICHED
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos
from fapi.helpers.math_helpers import gauss_score
from functools import partial
from pprint import pprint
async def history_alg(main_questions,secondary_questions):
    loop = asyncio.get_running_loop()
    distance=main_questions.distance*1000
    budget= main_questions.budget
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    experience_type=secondary_questions.experienceType
    location_types=secondary_questions.locationTypes
    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=distance
    )
    loc_restr = LocationRestriction(circle=circle)

    historyTypes = [
        {
      "key": key.strip(),
      **CATEGORY_CONFIG[key.strip()]
    }
        for key in location_types
    ]

    yield {
        "stage": "pas 1",
        "info": "Cautam locatii din zona in care te afli..."
    }

    raw_data=await fetch_places(historyTypes,loc_restr,EXTRA)
    
    yield{
            "stage": "pas 2",
            "info": "pregatim locatiile si le filtram..."
        }
    
    ratios=[0.35,0.35,0.2,0.1]
    criteria_classification=["+","+","-","+"]
    needs_normalization=[False,False,True,False]

    helpers_enrich=[
                    solve_photos]
    helpers_score=[partial( history_score_corr,exp_type=experience_type,score_map=EXTRA["QUERY_SCORE_MAP"]),
        partial(rating_score,condition=3.6,z=1.4),
                   partial(dist,userLat=latitude,userLong=longitude,condition=2800,radius=distance,ratio=1.5),
                   partial(price_score,budget=budget,sigma=0.45),
                   ]
    
    cleaned_data=await enrich_all(raw_data,ENRICHED,helpers_enrich,CATEGORY_CONFIG)
    
    for history_type,places in cleaned_data.items():
        loc_score_results = await loop.run_in_executor(
            DEFAULT_THREAD_POOL,
            compute_score,
            places,
            helpers_score,
            ratios,
            criteria_classification,
            needs_normalization,
            0.7
            
        )
        cleaned_data[history_type]=loc_score_results
    
    yield {
        "stage": "final",
        "data": cleaned_data
    }




def history_score_corr(place,exp_type,score_map):
    score_map=score_map
    highlight=None
    query=place.get("search_QUERY","")
    print("nume:",place.get("display"))
    print("asta e queryy:",query)
    print("types:",place.get("types"))
    if not query:
        print("buna din query")
        raise Exception()
    score=score_map.get(query)
    if not score:
        print("buna din score")
        raise Exception()
    if score>0.7:
        highlight="Arta si experienta vizuala de neuitat!"
    if score<0.35:
        highlight="Locatia aceasta ofera o experienta culturala si istorica importanta!"
    
    base_score=gauss_score(score,exp_type,sigma=0.3)

    if not base_score:
        print("sal din base score")
        raise Exception()
    
    
    return "historyCorr",base_score,highlight



    