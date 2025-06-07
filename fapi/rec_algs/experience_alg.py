import asyncio
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center
from fapi.constants.experience_config import CATEGORY_CONFIG,EXTRA,ENRICHED
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos
from fapi.routes.google_routes import get_weather
from fapi.helpers.math_helpers import gauss_score
from functools import partial



async def experience_alg(main_questions,secondary_questions):
    loop = asyncio.get_running_loop()
    distance=main_questions.distance*1000
    budget= main_questions.budget
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    adrenalineLvL=fix_Value(secondary_questions.adrenaline)
    indoor=fix_Value(secondary_questions.indoorOutdoor)
    physicalLvl=secondary_questions.physical
    try:
        wheater=await get_weather(latitude,longitude)
    except:
        raise Exception()

    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=distance
    )
    loc_restr = LocationRestriction(circle=circle)

    Types =[ {
      "key": "Experiente",
      **CATEGORY_CONFIG["Experiente"]
    }]

    remove_types(Types,indoor,wheater)

    
    yield {
        "stage": "pas 1",
        "info": "Cautam locatii din zona in care te afli..."
    }

    raw_data=await fetch_places(Types,loc_restr,EXTRA)
    
    yield{
            "stage": "pas 2",
            "info": "pregatim locatiile si le filtram..."
        }
    
    ratios=[0.25,0.25,0.1,0.2,0.1,0.1]
    criteria_classification=["+","+","+","+","-","+"]
    needs_normalization=[False,False,False,False,True,False]

    helpers_enrich=[
                    solve_photos]
    helpers_score=[partial( score_adrenalin,adrenalineLvl=adrenalineLvL,map=EXTRA["type_config"]),
                   partial( score_phyisical,phyisical=physicalLvl,map=EXTRA["type_config"]),
                   partial( score_indoor,indoor=indoor,map=EXTRA["type_config"]),
        partial(rating_score,condition=3.6,z=1.4),
                   partial(dist,userLat=latitude,userLong=longitude,condition=2800,radius=distance,ratio=1.5),
                   partial(price_score,budget=budget,sigma=0.45),
                   ]
    
    cleaned_data=await enrich_all(raw_data,ENRICHED,helpers_enrich,CATEGORY_CONFIG)
    
    for type,places in cleaned_data.items():
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
        cleaned_data[type]=loc_score_results
    
    yield {
        "stage": "final",
        "data": cleaned_data
    }




def fix_Value(option):

    if option == "Da" or option=="indoor":
        return 1
    elif option == "Nu" or option=="outdoor":
        return 0
    else:
        return 0.5

def score_adrenalin(place,adrenalineLvl,map):
    highlight=None
    query=place.get("search_QUERY","")
    
    if not query:
        print("Nu am query la adrenaline")
        raise Exception()
    
    adrenalinePlace=map.get(query,{}).get("adrenaline",None)
    if adrenalinePlace is None:
        print("Nu  adrenaline in andrelalineScore")
        raise Exception()
    
    if adrenalinePlace>=0.7:

        highlight="Locatie perfecta pentru distractie plina de adrenalina!"

    adrenalinScore=gauss_score(adrenalinePlace,adrenalineLvl,sigma=0.3)

    return "adrenalinScore",adrenalinScore,highlight

def score_phyisical(place,phyisical,map):
    highlight=None
    query=place.get("search_QUERY","")

    if not query:
        print("Nu am query la pyshical")
        raise Exception()
    
    physicalPlace=map.get(query,{}).get("physical",None)
    if physicalPlace is None:
        print("Nu  pysical la pyshical score")
        raise Exception()
    
    if physicalPlace>=0.7:

        highlight="Locatie perfecta pentru distractie plina de adrenalina!"

    physicalScore=gauss_score(physicalPlace,phyisical,sigma=0.3)

    return "physicalScore",physicalScore,highlight

def score_indoor(place,indoor,map):
    highlight=None
    query=place.get("search_QUERY","")

    if not query:
        print("Nu am query la indoor")
        raise Exception()
    
    indoorPlace=map.get(query,{}).get("indoor",None)
    if indoorPlace is None:
        print("Nu  indoorPlace in indoor")
        raise Exception()
    
    if indoorPlace>=0.7:

        highlight="Locatie perfecta pentru distractie plina de adrenalina!"

    indoorScore=gauss_score(indoorPlace,indoor,sigma=0.3)

    return "indoorScore",indoorScore,highlight


def remove_types(Types,indoor,wheater):

    to_remove=[]
    map=EXTRA["type_config"]

    is_day=wheater.get("is_day")
    temp=wheater.get("temp")
    max_temp=wheater.get("max_temp")
    types=Types[0]
    for type in types["nearby_search_non_prim_types"]:
        
        indoor_of_type=map.get(type).get("indoor")
        needs_wheater=map.get(type).get("needs_wheater",None)

        if indoor==1 and indoor_of_type==0:
            to_remove.append(type)
        
        elif indoor==0 and indoor_of_type==1:

            to_remove.append(type)

        if needs_wheater is not None and needs_wheater==0 :

            if is_day and temp>8:

                to_remove.append(type)

            elif not is_day and max_temp>8:

                to_remove.append(type)

        elif needs_wheater is not None and needs_wheater==1 :

            if is_day and temp<23:

                to_remove.append(type)

            elif not is_day and max_temp<23:

                to_remove.append(type)

    lst = types["nearby_search_non_prim_types"]
    types["nearby_search_non_prim_types"][:] = [
        t for t in lst if t not in to_remove
    ]






    