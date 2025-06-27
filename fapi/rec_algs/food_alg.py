
import asyncio
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center
from fapi.constants.food_config import CATEGORY_CONFIG,EXTRA,ENRICHED
from fapi.constants.general_config import PRICE_LEVEL_MAP
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos,location_restriction
from fapi.helpers.math_helpers import gauss_score
from functools import partial
from pprint import pprint
async def food_alg(main_questions,secondary_questions,condition=1500,**kwargs):
    cancellation_event = kwargs.get("cancellation_event")
    max_places=kwargs.get("max_places",12)
    min_places=kwargs.get("min_places",10)
    loop = asyncio.get_running_loop()
    distance=int(main_questions.distance*1000)
    budget= main_questions.budget
    type=main_questions.category
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    food_types=secondary_questions.foodTypes
    meal_type=secondary_questions.mealType
    vegan=secondary_questions.veganOptions
    outdoor=secondary_questions.outdoor
    restaurant_type=secondary_questions.locationType

    randomize=True if type!="Itinerariu" else False

    dist_condition=1000 if type!="Itinerariu" else 50

    loc_restr=location_restriction(latitude,longitude,distance,randomize=randomize)

    

    Types = [
        {
      "key": key.strip(),
      **CATEGORY_CONFIG[key.strip()]
    }
        for key in food_types
    ]

    
    yield {
        "stage": "pas 1",
        "info": "Cautam locatii din zona in care te afli..."
    }

    raw_data=await fetch_places(Types,loc_restr,EXTRA,cancellation_event=cancellation_event)
    
    yield{
            "stage": "pas 2",
            "info": "pregatim locatiile si le filtram..."
        }
    
    ratios=[0.1,0.15,0.1,0.15,0.15,0.15,0.2]
    criteria_classification=["+","+","-","+","+","+","+"]

    helpers_enrich=[partial(restaurant_type_enrich,map=PRICE_LEVEL_MAP),
                    solve_photos]
    helpers_score=[
        partial(price_score,budget=budget,sigma=0.45),
        partial(rating_score,condition=3.6,z=1.4),
        partial(dist,userLat=latitude,userLong=longitude,condition=dist_condition,radius=distance,ratio=1.5),
        partial(vegan_score,vegan=vegan),
        partial(outdoor_score,outdoor=outdoor),
        partial(meal_type_score,meal_type=meal_type),
        partial(restaurant_type_score,restaurant_type_input=restaurant_type),
        
        
                   
                   
                   ]
    
    cleaned_data,banned_places=await enrich_all(raw_data,ENRICHED,helpers_enrich,CATEGORY_CONFIG,cancellation_event=cancellation_event)
    
    for type,places in cleaned_data.items():
        loc_score_results = await loop.run_in_executor(
            DEFAULT_THREAD_POOL,
            compute_score,
            places,
            helpers_score,
            ratios,
            criteria_classification,
            banned_places,
            cancellation_event,
            0.5,
            max_places,
            min_places,
            
        )
        cleaned_data[type]=loc_score_results
    
    yield {
        "stage": "final",
        "data": cleaned_data
    }

#helperi score

def meal_type_score(place,meal_type):
    highlight=None
    meal_type_s=None
    types=place.get("types")
    if meal_type=="Mic-dejun":
        place_serves=place.get("breakfast","")
        if place_serves=="":
            meal_type_s=0.4
        else:
            if place_serves:
                highlight="Acest loc serveste micul-dejun!"
                meal_type_s=1
            else:
                meal_type_s=0
        
    if meal_type=="Pranz":
        place_serves=place.get("lunch","")
        if place_serves=="":
            meal_type_s=0.7
        else:
            if place_serves:
                meal_type_s=1
                highlight="Acest loc serveste masa de pranz!"
            else:
                meal_type_s=0

    if meal_type=="Cina":
        place_serves=place.get("dinner","")
        if place_serves=="":
            meal_type_s=0.7
        if place_serves=="" and "fast_food_restaurant" in types:
            meal_type_s=0.5
        else:
            if place_serves:
                highlight="Acest are in program servirea cinei!"
                meal_type_s=1
            else:
                meal_type_s=0
            
        
    
    return "mealTypeScore",meal_type_s,highlight
def outdoor_score(place,outdoor):
    highlight=None
    outdoor_s=None
    has_outdoor_seating=place.get("outdoor","")
    
    if has_outdoor_seating=="" or has_outdoor_seating==False:

        outdoor_s=0.4

        highlight="Restaurantul nu specifica daca detine o terasa sau nu. Verficati inainte."

    else:

        outdoor_s=1

        highlight="Restaurantul are terasa!"

    if not outdoor:
        outdor_s=0

    return "outdoor_score",outdoor_s,highlight



def vegan_score(place,vegan):
    highlight=None
    vegan_s=None
    types=place.get("types",[])
    primary_type=place.get("primaryType","")
    serves_vegan=place.get("vegan","")
    if not types:
        print("eroare la vegan score")
        raise Exception()
    
    if not vegan:
        vegan_s=0
        if "vegetarian_restaurant" or "vegan_restaurant" in types or serves_vegan:
            highlight="Acest restaurant are optiuni vegane."
    
    else:

        if serves_vegan=="" or serves_vegan=="false":
            highlight="Restaurantul nu specifica daca ofera optiuni vegane sau nu! Verificati inainte."
            vegan_s=0.3

        if serves_vegan!="":

            if serves_vegan:
                highlight="Acest restaurant are explicit in meniu optiuni vegane!"
                vegan_s=0.8

            

        if "vegetarian_restaurant" or "vegan_restaurant" in types:
            highlight="Acest restaurant are explicit in meniu optiuni vegane!"
            vegan_s=0.8

        if primary_type in ("vegetarian_restaurant", "vegan_restaurant"):
            highlight="Acest restaurant are specific vegetarian, cu o multime de optiuni!"
            vegan_s=1

        

    return "veganScore",vegan_s,highlight

def restaurant_type_enrich(place,map):
    restaurant_type=None
    price_level=place.get("priceLevel","")
    types=place.get("types",[])
    reservable=place.get("reservable","")
    highlight=None
    if "fast_food_restaurant" in types:
        restaurant_type=0
        highlight="Restaurantul este de tip fast-food."
    else:
        restaurant_type=0.35
        highlight="Restaurantul nu este de tip fast-food dar s-ar putea sa nu aiba rezervare sau servire la masa. Verificati inainte."
    if reservable!="" and reservable:
        highlight="Restaurantul ofera rezervare si servire!"
        restaurant_type=0.5
        if price_level and map.get(price_level)>=0.75:
            highlight="Restaurantul este exclusivist!"
            restaurant_type=0.7

    if "fine_dining_restaurant" in types:
        highlight="Restaurantul este exclusivist, de tip fine-dining!"
        restaurant_type=1

    return "restaurant_type",restaurant_type,highlight



def restaurant_type_score(place,restaurant_type_input):
    
    restaurant_type=place.get("restaurant_type")
    restaurant_score=gauss_score(restaurant_type,restaurant_type_input,sigma=0.2)

    return "restaurant_score",restaurant_score,None







