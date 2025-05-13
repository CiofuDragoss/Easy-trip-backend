import asyncio
import math
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.helpers.math_helpers import wilson_score,gauss_score,haversine_distance
from fapi.schemas import LocationRestriction,Circle,Center,NearbySearch,TextSearch
from fapi.routes.google_routes import safe_google_details,google_nearby_search,google_text_search
import inspect
from functools import partial
from pprint import pprint
from fapi.helpers.math_helpers import wilson_score,gauss_score,haversine_distance
async def fetch_places(category,loc_restr,category_extra):
    raw_data=[]
    for category_type in category:
        entry = {
        "category_type": category_type["key"],
        "nearby_responses": [],
        "text_responses": []
    }
        nearby_tasks=[]
        text_tasks=[]

        for t in category_type["nearby_type"]:
            req = NearbySearch(
                locationRestriction=loc_restr,
                excludedTypes= category_type["excludedTypes"].get(t, []),
                includedPrimaryTypes=[t],
                fieldMask=category_extra["Mask"]
            )
            nearby_tasks.append(google_nearby_search(req))

            

        for q in category_type["text_query"]:
            req=TextSearch(
                textQuery=q,
                locationBias=loc_restr,
                fieldMask=category_extra["Mask"]


            )
            text_tasks.append(google_text_search(req))
            
        entry["nearby_responses"] = await asyncio.gather(*nearby_tasks)
        entry["text_responses"] = await asyncio.gather(*text_tasks)
        raw_data.append(entry)
    
   
    return raw_data

def get_data(data,path,default=None):
    for key in path:
        
        data=data.get(key,default)
        if data is default:
            return default
    return data

async def enrich_place(place,extract,category_type,search_type,*args,
    **kwargs):
    enriched={}
    enriched.update({
        "category":    category_type,
        "search_mode": search_type,
        "highlights":  [], 
        **kwargs
    })
    for var_name,(path_str,fallback) in extract.items():

        path=path_str.split(".")

        enriched[var_name]=get_data(place,path,fallback)
    for fn in args:
        result=fn()
        if inspect.isawaitable(result):
            var_name,value,highlight=await result
        else:
            var_name,value,highlight=result
        if highlight:
            enriched["highlights"].append(highlight)
        enriched[var_name]=value

    

    return enriched

def verify_place(category_type,key,config,place):
    types=place.get("types",[])
    display = place.get("displayName", {}).get("text", "").lower()
    if key=="nearby_search":
        included=config[category_type]["nearbyIncludedTypes"]
        bannedWords=config[category_type]["bannedWordsNearby"]
        if not any(t in included for t in types) and included:
            return False
        if any(t in display for t in bannedWords) and bannedWords:
            return False
        
    else:
        included=config[category_type]["textIncludedTypes"]
        excluded=config[category_type]["textExcludedTypes"]
        bannedWords=config[category_type]["bannedWordsText"]
        types=place.get("types",[])
        if not any(t in included for t in types) and included:
            return False
        if any(t in excluded for t in types) and excluded:
            return False
        if any(t in display for t in bannedWords) and bannedWords:
            return False
    
    return True

async def enrich_all(raw_data,extract,extra_funcs,config):
    enriched_places={}
    
    


    for entry in raw_data:
        tasks = []
        placeId_set=set()
        print("lollll din enrich")
        category_type=entry["category_type"]
        print(category_type)
        for key, responses in [
            ("nearby_search", entry["nearby_responses"]),
            ("text_search",   entry["text_responses"])
        ]:
            for resp in responses:
                for place in resp.get("places", []):
                    place_id=place.get("id")
                    
                    if place_id in placeId_set:
                        
                        continue
                    
                    
                    if not verify_place(category_type,key,config,place):
                        
                        continue
                    
                    placeId_set.add(place_id)
                    
                    helpers = [partial(fn, place) for fn in extra_funcs]
                    tasks.append(enrich_place(place,extract,category_type,key,*helpers))

        enriched = await asyncio.gather(*tasks,return_exceptions=True)

        

        enriched_places[category_type] = [
            r for r in enriched
            if not isinstance(r, Exception)
        ]


    return enriched_places


def compute_score(cleaned_data,helpers,ratios):
    loc_score_results = []
    final_cleaned_places=[]
    for place in cleaned_data:
        place.setdefault("highlights", [])
        loc_scores={}
        score=0
        skip=False
        for fn,ratio in zip(helpers,ratios):
            try:
                var_name,value,highlight=fn(place)
                score+=ratio*value
                if highlight:
                    place["highlights"].append(highlight)
            except:
                skip=True
                break
            
            loc_scores[var_name]=value
        if skip:
            continue
        loc_scores["placeId"]=place.get("placeId")
        loc_scores["mainScore"]=round(score/len(ratios),5)
        loc_score_results.append(loc_scores)
    
    score_map = {
        entry["placeId"]: {
            k: v for k, v in entry.items() if k != "placeId"
        }
        for entry in loc_score_results
    }
    
    for place in cleaned_data:
        id=place.get("placeId")
        scores=score_map.get(id,None)

        final_place={}

        if scores is not None:
            final_place={**place,**scores}
            
            final_cleaned_places.append(final_place)

    sorted_final_places = sorted(
        final_cleaned_places,
        key=lambda p: p["mainScore"],
        reverse=True
    )

    n=len(sorted_final_places)
    cutoff = math.ceil(n * 0.3) if math.ceil(n*0.3)<8 else 7
    top_locations=sorted_final_places[:cutoff]

    return top_locations





    
   
    
   

  