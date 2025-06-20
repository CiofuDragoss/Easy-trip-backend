import asyncio
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center
from fapi.constants.experience_config import CATEGORY_CONFIG,EXTRA,ENRICHED
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos
from fapi.routes.google_routes import get_weather
from fapi.helpers.math_helpers import gauss_score
from functools import partial



async def experience_alg(main_questions,secondary_questions,**kwargs):
    nearby_excluded_types=kwargs.get("nearby_excluded_types", None)
    max_places=kwargs.get("max_places",12)
    min_places=kwargs.get("min_places",10)
    kwargs.get("nearby_excluded_types", None)
    loop = asyncio.get_running_loop()
    distance=int(main_questions.distance*1000)
    budget= main_questions.budget
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
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

    remove_types(Types,indoor,wheater,nearby_excluded_types)

    print("Types:", Types[0]["nearby_search_non_prim_types"])
    print("Types main :", Types[0]["nearby_type"])
    yield {
        "stage": "pas 1",
        "info": "Cautam locatii din zona in care te afli..."
    }

    raw_data=await fetch_places(Types,loc_restr,EXTRA)
    
    yield{
            "stage": "pas 2",
            "info": "pregatim locatiile si le filtram..."
        }
    
    ratios=[0.3,0.3,0.15,0.15,0.1]
    criteria_classification=["+","+","+","-","+"]
    needs_normalization=[False,False,False,True,False]

    helpers_enrich=[partial(enrich_duration,map=EXTRA["type_config"]),
                    solve_photos]
    helpers_score=[
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
            0.8,
            max_places,
            min_places
            
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
    if physicalPlace<=0.3:
        highlight="Locatia nu necesita activitate fizica!"
    
    if physicalPlace>=0.7:

        highlight="Locatia necesita un nivel fizic mai ridicat!"

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

        highlight="Locatie este indoor!"

    indoorScore=gauss_score(indoorPlace,indoor,sigma=0.3)

    return "indoorScore",indoorScore,highlight

def enrich_duration(place,map):
    query=place.get("search_QUERY","")
    duration=60
    if not query:
        print("Nu am query la duration")
        raise Exception()
    
    indoorPlace=map.get(query,{}).get("duration",None)
    if indoorPlace is None:
        print("Nu  durationPlace in duration")
        raise Exception()
    
    return "duration",duration,None
    


def remove_types(Types,indoor,wheater,banned_types):

    to_remove=[]
    map=EXTRA["type_config"]

    is_day=wheater.get("is_day")
    temp=wheater.get("temp")
    print("asta e temp",temp)
    max_temp=wheater.get("max_temp")
    print("asta e max_temp",max_temp)
    types=Types[0]
    for type in types["nearby_search_non_prim_types"]+types["nearby_type"]:
        print("tipul este : ",type)
        
        indoor_of_type=map.get(type).get("indoor")
        needs_weather=map.get(type).get("needs_weather",None)
        print("needs_wheater",needs_weather)
        if indoor==1 and indoor_of_type==0:
            to_remove.append(type)
            
        elif indoor==0 and indoor_of_type==1:

            to_remove.append(type)
           
        if needs_weather is not None and needs_weather==0 :
           
            if is_day and temp>8:
                print("sunt aici",type)
                to_remove.append(type)
                
            elif not is_day and max_temp>8:

                to_remove.append(type)
                
            
        elif needs_weather is not None and needs_weather==1 :
            
            if is_day and temp<23:
                print("sunt aiciiii",type)
                to_remove.append(type)
                

            elif not is_day and max_temp<23:

                to_remove.append(type)
                
    if banned_types:
        to_remove.append(type)
    lst = types["nearby_search_non_prim_types"]
    types["nearby_search_non_prim_types"][:] = [
        t for t in lst if t not in to_remove
    ]

    lst = types["nearby_type"]
    types["nearby_type"][:] = [
        t for t in lst if t not in to_remove
    ]

    







    