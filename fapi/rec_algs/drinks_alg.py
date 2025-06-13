
import asyncio
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center
from fapi.constants.drink_config import CATEGORY_CONFIG,EXTRA,ENRICHED
from fapi.constants.general_config import PRICE_LEVEL_MAP
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos
from fapi.helpers.math_helpers import gauss_score
from functools import partial
from pprint import pprint
async def drinks_alg(main_questions,secondary_questions):
    loop = asyncio.get_running_loop()
    distance=main_questions.distance*1000
    budget= main_questions.budget
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    group=secondary_questions.groupType
    drink_type=secondary_questions.drinkTypes
    location_types=secondary_questions.locationTypes
    
    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=distance
    )
    loc_restr = LocationRestriction(circle=circle)

    

    Types = [
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

    raw_data=await fetch_places(Types,loc_restr,EXTRA)
    
    yield{
            "stage": "pas 2",
            "info": "pregatim locatiile si le filtram..."
        }
    

    helpers_enrich = [
    

    enrich_coffee,
    enrich_tea,
    enrich_juices,
    enrich_desserts,
    enrich_gelato,
    enrich_wine,
    enrich_cocktails,
    enrich_beer,
    solve_photos
]
    ratios=[0.3,0.15,0.15,0.25,0.15]
    criteria_classification=["+","-","+","+","+"]
    needs_normalization=[False,True,False,False,False]
    helpers_score=[
        
        
        partial(rating_score,condition=3.6,z=1.4),

                   partial(dist,userLat=latitude,userLong=longitude,condition=2800,radius=distance,ratio=1.5),
                   partial(price_score,budget=budget,sigma=0.45),
                   partial(score_drink_type,drink_type=drink_type),
                   partial(score_group,group=group)
                   
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
            0.5
            
        )
        cleaned_data[type]=loc_score_results
    
    yield {
        "stage": "final",
        "data": cleaned_data
    }

def enrich_coffee(place):
    coffee=place.get("servesCoffee","")
    types=place.get("types")
    coffe_score=0
    highlight=None
    if  coffee or "cafe" in types:
        coffe_score=1
        highlight="Cafea."

    return "Cafea",coffe_score,highlight
def enrich_beer(place):
    beer=place.get("servesBeer","")
    types=place.get("types")
    beer_score=0
    highlight=None
    if  beer or "bar" in types:
        beer_score=1
        highlight="Bere."

    return "Bere",beer_score,highlight

def enrich_cocktails(place):
    cocktail=place.get("servesCocktails","")
    types=place.get("types")
    cocktail_score=0
    highlight=None
    if "bar" in types:
        cocktail_score=0.75
    if  cocktail:
        cocktail_score=1
        highlight="Cocktailuri."

    return "Cocktailuri",cocktail_score,highlight

def enrich_wine(place):
    wine=place.get("servesWine","")
    types=place.get("types")
    wine_score=0
    highlight=None
    if  wine:
        wine_score=0.75
        highlight="Vin."
    elif "wine_bar" in types:
        wine_score=1
        highlight="Selectie larga de vinuri."
    return "Vin",wine_score,highlight


def enrich_desserts(place):
    dessert=place.get("servesDessert","")
    types=place.get("types")
    dessert_score=0
    highlight=None
    if  dessert:
        dessert_score=0.6
        highlight="Dulciuri."

    elif "confectionery" in types or "dessert_restaurant" in types or "donut_shop" in types or "candy_store" in types:
        dessert_score=1
        highlight="Locatie specializata in dulciuri si deserturi."

    return "Dulciuri",dessert_score,highlight


def enrich_gelato(place):
    types=place.get("types")
    primary_type=place.get("primaryType","")
    gelato_score=0
    highlight=None
    if "ice_cream_shop" in types:
        gelato_score=0.7
        highlight="Inghetata."

    elif primary_type=="ice_cream_shop":
        gelato_score=1
        highlight="Locatie specializata in inghetata."

    return "Inghetata",gelato_score,highlight

def enrich_juices(place):
    types=place.get("types")
    juices_score=0
    highlight=None

    if "cafe" in types or "bar" in types:
        highlight="Este posibil ca locatia sa serveasca sucuri naturale. Verificati inainte."
        juices_score=0.6
    if "juice_shop" in types:
        juices_score=1
        highlight="Sucuri fresh."
    
    
    return "Sucuri de fructe",juices_score,highlight

def enrich_tea(place):
    types=place.get("types")
    tea_score=0
    highlight=None
    if "cafe" in types or "bar" in types:
        tea_score=0.7
        highlight="Este posibil ca locatia sa serveasca ceaiuri. Verificati inainte."

    if "tea_house" in types:
        tea_score=1
        highlight="Ceaiuri."
    
    

    return "Ceai",tea_score,highlight


def score_drink_type(place,drink_type):
    highlight=None
    drink_score=0
    place_drink_score=place.get(drink_type)
    if drink_type!="Nu conteaza":
        
        drink_score=gauss_score(1,place_drink_score,sigma=0.15)

    return "drink_score",drink_score,highlight

def score_group(place,group):
    highlight=None
    goodForGroup=place.get("group","")
    group_score=0
    if group and goodForGroup!="":

        if goodForGroup:

            highlight="Locatie perfecta pentru grupuri numeroase!"

            group_score=1

        else:
            highlight="Locatia nu este potrivita pentru grupuri!."
            group_score=0

    elif group and goodForGroup=="":

        group_score=0.75

        highlight="Verificati inainte daca locatia este potrivita pentru grupuri."

            
    return "group_score",group_score,highlight