import asyncio
import math
import pandas as pd
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.helpers.math_helpers import wilson_score,gauss_score,haversine_distance
from fapi.schemas import LocationRestriction,Circle,Center,NearbySearch,TextSearch
from fapi.routes.google_routes import safe_google_details,google_nearby_search,google_text_search
import inspect
from functools import partial
from pprint import pprint
from fapi.helpers.math_helpers import wilson_score,gauss_score,haversine_distance
from fapi.constants.general_config import PRICE_LEVEL_MAP
import traceback

def solve_photos(place):
    photos=place.get("photos","")
    highlight=None
    if photos:
        photos=photos[:4]
        photo_names=[photo.get("name") for photo in photos if photo.get("name")]
        return "photos",photo_names,highlight
    raise Exception()



def rating_score(place,condition=None,z=1.4):
    highlight=None
    rating=place.get("rating")
    if condition and rating<condition:
         raise Exception()
    ratingCount=place.get("ratingCount")
    ratingScore=wilson_score(rating,ratingCount,z)
    if ratingScore>0.85:
        highlight="Locatia aceasta are ratinguri excelente."
    return "ratingScore",round(ratingScore,5),highlight

def dist(place,userLat,userLong,radius,condition=10,ratio=1.5):
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
            
            nearby_tasks.append((google_nearby_search(req),t))

            
        for i in category_type.get("nearby_search_non_prim_types",[]):
            req = NearbySearch(
                locationRestriction=loc_restr,
                excludedTypes= category_type["excludedTypes"].get(i, []),
                includedTypes=[i],
                fieldMask=category_extra["Mask"]
            )
            
            nearby_tasks.append((google_nearby_search(req),i))

        for q in category_type["text_query"]:
            req=TextSearch(
                textQuery=q,
                locationBias=loc_restr,
                fieldMask=category_extra["Mask"]


            )
            text_tasks.append((google_text_search(req),q))
            
        

        nearby_coros, nearby_keys = zip(*nearby_tasks) if nearby_tasks else ([], [])
        text_coros,   text_keys   = zip(*text_tasks)   if text_tasks   else ([], [])

        nearby_results = await asyncio.gather(*nearby_coros) if nearby_coros else []
        text_results   = await asyncio.gather(*text_coros)   if text_coros   else []

        for resp, t in zip(nearby_results, nearby_keys):
            
            
            entry["nearby_responses"].append({
                "search_QUERY":   t,         
                "places": resp.get("places", [])
            })
            
        
        for resp, q in zip(text_results, text_keys):
            entry["text_responses"].append({
                "search_QUERY":  q,         
                "places": resp.get("places", [])
            })

            
        
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
            fn=partial(fn, enriched)
            result=fn()
            if inspect.isawaitable(result):
                var_name,value,highlight=await result
            else:
                var_name,value,highlight=result
            if highlight:
                enriched["highlights"].append(highlight)
            
            enriched[var_name]=value
    
    print("\n")
    
    
    print("tip principal",enriched["primaryType"])
    print("price range",enriched["priceLevel"])
    print("display:",enriched["display"])
    print("tipuri: ",enriched["types"])
    print("LiveMusic:",       enriched.get("liveMusic", ""))
    print("Sports:",   enriched.get("sports", ""))
    print("openingHours",enriched["openingHours"])
    
    return enriched

def verify_place(category_type,key,config,place,query):
    types=place.get("types",[])
    primary_type=place.get("primaryType")
    display = place.get("displayName", {}).get("text", "").lower()
    if key=="nearby_search":
        included=config[category_type].get("nearbyIncludedTypes").get(query,[])
        excludedPrimaryTypes=config[category_type].get("nearbyExcludedPrimaryTypes",[])
        bannedWords=config[category_type]["bannedWordsNearby"]
        if not any(t in included for t in types) and included:
            return False
        
        if excludedPrimaryTypes and primary_type in excludedPrimaryTypes:
            return False
        if any(t in display for t in bannedWords) and bannedWords:
            print("eliminare in nearby de la banned words")
            return False
        
        
    else:
        included=config[category_type]["textIncludedTypes"]
        excluded=config[category_type]["textExcludedTypes"]
        bannedWords=config[category_type]["bannedWordsText"]
        excludedPrimaryTypes=config[category_type].get("textExcludedPrimaryTypes",[])
        if not any(t in included for t in types) and included:
            print("eliminare in text search de la included")
            return False
        if any(t in excluded for t in types) and excluded:
            print("eliminare in text search de la excluded")
            return False
        if excludedPrimaryTypes and primary_type in excludedPrimaryTypes:
            return False
        if any(t in display for t in bannedWords) and bannedWords:
            print("eliminare in text search de la banned words")
            return False
    
    return True

async def enrich_all(raw_data,extract,extra_funcs,config):
    enriched_places={}
    
    


    for entry in raw_data:
        tasks = []
        placeId_set=set()
        
        category_type=entry["category_type"]
        print("categoriee",category_type)
        for key, responses in [
            ("nearby_search", entry["nearby_responses"]),
            ("text_search",   entry["text_responses"]),
            
            
        ]:
            
            for resp in responses:
                query=resp.get("search_QUERY","")
                for place in resp.get("places", []):
                    place_id=place.get("id")
                    
                    if place_id in placeId_set:
                        print("eliminare in placeSET")
                        continue
                    
                    
                    if not verify_place(category_type,key,config,place,query):
                        
                        continue
                    
                    placeId_set.add(place_id)
                    
                    tasks.append(enrich_place(place,extract,category_type,key,*extra_funcs,search_QUERY=query))

        enriched = await asyncio.gather(*tasks,return_exceptions=True)
        
        

        enriched_places[category_type] = [
            r for r in enriched
            if not isinstance(r, Exception)
        ]

    
    return enriched_places


def compute_score(cleaned_data,helpers,ratios,criteria_classification,needs_normalization,v=0.5,max_places=2,min_places=6):
    if not cleaned_data:
        print("sal")
        return []
    loc_score_results = []
    final_cleaned_places=[]
    for place in cleaned_data:
        
        place.setdefault("highlights", [])
        loc_scores={}
        
        skip=False
        for fn,ratio,classification,normalization in zip(helpers,ratios,criteria_classification,needs_normalization,):
           
            try:
               
                var_name,value,highlight=fn(place)
                if highlight:
                    place["highlights"].append(highlight)
                
            except Exception as e:
                print(e)
                skip=True
                break
            
            loc_scores[var_name]=value
            loc_scores[var_name+'_ratio']=ratio
            loc_scores[var_name+"_clasif"]=classification
            loc_scores[var_name+"_norm"]=normalization
        if skip:
            continue

        loc_scores["placeId"]=place.get("placeId")
        loc_score_results.append(loc_scores)

    if not loc_score_results :
        
        return []
    
    


    #start VIKOR

    df = pd.DataFrame(loc_score_results)
    df.set_index("placeId", inplace=True)
    if df.empty:
        return []
    
    all_columns = list(df.columns)
    criteria=[]

    for col in all_columns:
        if col.endswith("_norm"):
            var_base=col[:-len("_norm")]
            criteria.append(var_base)

    #normalizam (daca este nevoie) conform clasificarii (benficiu sau cost (+ respectiv -)) si calculam distantele
    for var in criteria:

        norm=f"{var}_norm"
        clasif=f"{var}_clasif"
        ratio=f"{var}_ratio"
        if df[norm].any():
            values=df[var].astype(float)
            fmin=values.min()
            fmax=values.max()

            span=fmax-fmin

            if df[clasif].eq("-").any():
                
                df[var]=(fmax-values)/span
                
            else:
                df[var]=(values-fmin)/span

        values=df[var].astype(float)
        ratio_val=df[ratio].iloc[0]
        fmax=values.max()
        fmin=values.min()

        df[var]=ratio_val*(fmax-values)/(fmax-fmin)

    
        
    #cleanup,nu mai avem nevoie de coloanele norm si clasif

    cols_to_remove = [col for col in all_columns if col.endswith("_norm") or col.endswith("_clasif") or col.endswith("_ratio")]

    df.drop(columns=cols_to_remove, inplace=True)

    df["S"]=df[criteria].sum(axis=1)
    df["R"]=df[criteria].max(axis=1)

    S_star=df["S"].min()
    S_minus=df["S"].max()
    R_star=df["R"].min()
    R_minus=df["R"].max()
    df.drop(columns=criteria,inplace=True)
    df["Q"]=(
        v*(df["S"]-S_star)/(S_minus-S_star)+(1-v)*(df["R"]-R_star)/(R_minus-R_star)
    )

    vikor_map = df.to_dict(orient="index")
    
    

    #END VIKOR
    score_map = {
        entry["placeId"]: {
            k: v for k, v in entry.items() if k != "placeId" and not k.endswith(("_norm", "_ratio", "_clasif"))
        }
        for entry in loc_score_results
    }
    
    
    for place in cleaned_data:
        id=place.get("placeId")
        scores=score_map.get(id,None)
        vikor_vars=vikor_map.get(id,None)
        final_place={}

        if scores is not None:
            final_place={**place,**scores,**vikor_vars}
            
            
            final_cleaned_places.append(final_place)

    if len(final_cleaned_places)==1:
        place=final_cleaned_places[0]
        id=place.get("placeId")
        vikor_vars=vikor_map.get(id)
        for key in vikor_vars:
            place.pop(key, None)
        
        return [place]
    final_cleaned_places.sort(key=lambda x: x["Q"])
    print("lungime final places:",len(final_cleaned_places))
    n=len(final_cleaned_places)
    cutoff = math.ceil(n * 0.5) if math.ceil(n*0.5)<max_places else min_places
    top_locations=final_cleaned_places[:cutoff]
    print("lungime top locs places:",len(top_locations))
    return top_locations



def location_restriction(latitude,longitude,distance):
    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=distance
    )
    loc_restr = LocationRestriction(circle=circle)

    return loc_restr


    
   
    
   

  