from fapi.helpers.math_helpers import wilson_score,gauss_score,haversine_distance
import asyncio
from fapi.constants.category_config import PRICE_LEVEL_MAP,SHOPPING_CATEGORY_CONFIG,SHOPPING_EXTRA
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center,NearbySearch,TextSearch
from fapi.routes.google_routes import google_details,google_nearby_search,google_text_search,resolve_img_urls
from pprint import pprint
import asyncio
def comppute_location_score(cleaned_data,budget,local,userLat,userLong,radius=3000):
    loc_score_results = []
    for place in cleaned_data:
        placeName=place.get("displayName")
        placeId=place.get("placeId")
        rating=place.get("rating")
        ratingCount=place.get("ratingCount")
        priceLevel=place.get("priceLevel")
        inMall=place.get("inMall")
        latitude=place.get("latitude")
        longitude=place.get("longitude")


        score=0
        priceScore=0
        localScore=gauss_score(inMall,local,sigma=0.4)
        dist=haversine_distance(latitude,longitude,userLat,userLong)
        distanceScore=gauss_score( max(dist, radius),radius,sigma=radius/1.5)
        ratingScore=wilson_score(rating,ratingCount)
        if float(place.get("rating","0"))<3.5:
                    continue
        
        if priceLevel:
                    price_level_value=PRICE_LEVEL_MAP[place.get("priceLevel")]
                    priceScore=gauss_score(price_level_value,budget,sigma=0.45)
        
        score+=45*ratingScore+30*localScore+10*priceScore+15*distanceScore

    loc_score_results.append({
            "name":       placeName,
            "MAIN_SCORE": round(score, 4),
            "priceScore": round(priceScore, 4),
            "ratingScore": round(ratingScore, 4),
            "localScore": round(localScore, 4),
            "rating":      rating,
            "ratingCount": ratingCount,
            "IN_MALL": inMall
        })
    
    return loc_score_results
        
        
        
    
async def enrich_all(raw_data):
    keywords = SHOPPING_EXTRA["keywords"]
    tasks = []

    for entry in raw_data:
        shopping_type=entry["shopping_type"]

        for nearby_result in entry["nearby_responses"]:
            for place in nearby_result.get("places",[]):
                tasks.append(enrich_place(place,keywords,shopping_type,"nearby_search"))

        for tr in entry["text_responses"]:
            for place in tr.get("places", []):
                tasks.append(
                    enrich_place(place, keywords, shopping_type,"text_search")
                )

    enriched = await asyncio.gather(*tasks)
    return enriched

async def enrich_place(place,keywords,shopping_type,search_type):
    display=place["displayName"]["text"]
    rating=place.get("rating",0)
    placeId=place.get("placeId",0)
    ratingCount = place.get("userRatingCount", 0)
    priceLevel = place.get("priceLevel","")
    latitude, longitude=place.get("location").get("latitude"),place.get("location").get("longitude")
    photos=place.get("photos")
    photo_names   = [p["name"] for p in photos]
    photo_urls    = await resolve_img_urls(photo_names)
    final_photos=[ {
      "url":    url,
      "width":  photo.get("widthPx"),
      "height": photo.get("heightPx"),
    } for photo,url in zip(photos,photo_urls) if url!=None]

    display_name_lower=display.lower()
    inMall=1 if any(kw.lower() in display_name_lower for kw in keywords) else 0

    
    if inMall==0 and place.get("containingPlaces"):
        tasks=[google_details(p["id"]) for p in place["containingPlaces"]]
        for detail in await asyncio.gather(*tasks):
            if "shopping_mall" in detail.get("types",[]):
                inMall=1
                break

    return {
        "placeId":placeId,
            "search_type":search_type,
            "shopping_type":shopping_type,
            "inMall":inMall,
            "latitude":latitude,
            "longitude":longitude,
            "photos":final_photos,
            "rating":rating,
            "ratingCount":ratingCount,
            "priceLevel":priceLevel,
            "displayName":display,
            "inMall":inMall,
        }


async def shopping_alg(main_questions,shopping_questions):

    loop = asyncio.get_running_loop()

    budget= main_questions.budget
    local=shopping_questions.shoppingLocType
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    
    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=3000
    )
    loc_restr = LocationRestriction(circle=circle)
    shoppingTypes = [
        {
      "key": key.strip(),
      **SHOPPING_CATEGORY_CONFIG[key.strip()]
    }
        for key in shopping_questions.shoppingExperience
    ]
    
    raw_data=await fetch_places(shoppingTypes,loc_restr)
    cleaned_data=await enrich_all(raw_data)
    pprint(cleaned_data)
    loc_score_results = await loop.run_in_executor(
        DEFAULT_THREAD_POOL,
        comppute_location_score,
        cleaned_data,
        budget,
        local,
        latitude,
        longitude,
        
    )
    pprint(loc_score_results)











async def fetch_places(shoppingTypes,loc_restr):
    raw_data=[]
    for shoppingType in shoppingTypes:
        entry = {
        "shopping_type": shoppingType["key"],
        "nearby_responses": [],
        "text_responses": []
    }
        nearby_tasks=[]
        text_tasks=[]

        for t in shoppingType["nearby_type"]:
            req = NearbySearch(
                locationRestriction=loc_restr,
                excludedTypes= shoppingType["excludedTypes"].get(t, []),
                includedPrimaryTypes=[t],
                fieldMask=SHOPPING_EXTRA["Mask"]
            )
            nearby_tasks.append(google_nearby_search(req))

            

        for q in shoppingType["text_query"]:
            req=TextSearch(
                textQuery=q,
                excludedTypes= shoppingType["textExcludedTypes"].get(q, []),
                locationBias=loc_restr,
                fieldMask=SHOPPING_EXTRA["Mask"]


            )
            text_tasks.append(google_text_search(req))
            
        entry["nearby_responses"] = await asyncio.gather(*nearby_tasks)
        entry["text_responses"] = await asyncio.gather(*text_tasks)
        raw_data.append(entry)
    return raw_data