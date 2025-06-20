import random
from datetime import datetime
from fapi.rec_algs.food_alg import food_alg
from fapi.rec_algs.shopping_alg import shopping_alg
from fapi.rec_algs.history_alg import history_alg
from fapi.rec_algs.experience_alg import experience_alg
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos,location_restriction
from fapi.constants.general_config import PRICE_LEVEL_MAP
from fapi.constants.executors import DEFAULT_THREAD_POOL
from fapi.schemas import LocationRestriction, Circle, Center,SecondaryQuestions,MainQuestions
from datetime import timedelta
import asyncio
from fapi.constants.Itinerary_config import CATEGORY_CONFIG_RELAX,EXTRA_RELAX,ENRICHED_RELAX
from functools import partial
async def first_period(day,budget,init_loc_restr,food_types,type_of_activity,intensity_activities, type_cultural,shopping, shopping_categories,intensity,wants_break,break_type,break_day_time,included=False):
    print("tipe cultural:",type_cultural)
    if not included:
        return {}
    final_first_period={}
    time=220+100*intensity
    start_hour=9

    food_place= await best_food_place(init_loc_restr,food_types,"Mic-dejun",budget,day,start_hour,intensity)
    duration_walk=calculate_walking_speed(food_place,intensity)
    activity_duration=50-13*intensity
    final_first_period[f"Incepeti ziua cu micul dejun la {food_place.get('display')}.Aveti de mers {duration_walk} de la locatia dumneavostra. Merita!"]=[food_place]
    time-=(activity_duration+duration_walk)

    start_hour+=round((activity_duration+duration_walk)/60)
    print("intensity",intensity)
    print("asta e ora",start_hour)
    print("time dupa mancare",time)

    init_loc_restr=get_new_restriction(food_place)
    first_activ=False
    while time>0:
        if first_activ and wants_break and break_day_time=="In prima parte a zilei":
            break_place= await call_break(init_loc_restr,break_type,budget,day,start_hour)
            duration_walk=calculate_walking_speed(break_place,intensity)
            activity_duration=50-20*intensity
            time-=(activity_duration+duration_walk)
            start_hour+=round((activity_duration+duration_walk)/60)
            init_loc_restr=get_new_restriction(break_place)
            final_first_period[f"Faceti o pauza de {break_type} la {break_place.get('display')}. Dureaza aproximativ {duration_walk} minute sa ajungeti."]=[break_place]
            wants_break=False
        elif first_activ and shopping:

            shopping_place=await best_shopping(budget,intensity,init_loc_restr,shopping_categories,day,start_hour)
            duration_walk=calculate_walking_speed(shopping_place,intensity)
            activity_duration=50-20*intensity
            time-=(activity_duration+duration_walk)
            start_hour+=round((activity_duration+duration_walk)/60)
            init_loc_restr=get_new_restriction(shopping_place)
            final_first_period[f"Veti gasi cele mai bune produse din categoria {shopping_place.get('category_type')} la  {shopping_place.get('display')}.Dureaza {duration_walk} sa ajungeti."]=[shopping_place]
            shopping=False
        activity_place=await best_experience_cultural(init_loc_restr,type_of_activity,type_cultural,budget,day,start_hour,intensity_activities,intensity)
        duration_walk=calculate_walking_speed(activity_place,intensity)
        activity_duration=activity_place.get("duration",70)-(activity_place.get("duration",70)/(1/10))*intensity if activity_place.get('place_type_cat')=="experience" else 65-25*intensity
        time-=(activity_duration+duration_walk)
        start_hour+=round((activity_duration+duration_walk)/60)
        init_loc_restr=get_new_restriction(activity_place)
        if not first_activ:
            key=f"Dupa ce terminati de servit micul-dejun, vizitati {activity_place.get('display')}, veti invata multe si veti avea parte de o experienta culturala de neuitat.Dureaza {duration_walk} sa ajungeti." if activity_place.get("place_type_cat")=="cultural" else f"Dupa ce terminati de servit micul-dejun, incepeti programul cu o experienta placuta la {activity_place.get('display')}.Dureaza {duration_walk} sa ajungeti."
        else:
            key=f"Continuati programul vizitand {activity_place.get('display')}.Bucurati-va de experienta culturala oferita de locatie.Dureaza {duration_walk} sa ajungeti." if activity_place.get("place_type_cat")=="cultural" else f"Continuati programul cu o experienta placuta la {activity_place.get('display')}.Dureaza {duration_walk} sa ajungeti."
        final_first_period[key]=[activity_place]
        first_activ=True
    return final_first_period








def create_food_sec_questions(food_types,meal_type):
    now=datetime.now()
    seed = int(now.timestamp())
    random.seed(seed)
    
    vegan           = 0
    outdoor         = 1
    restaurant_type = random.uniform(0.55, 1)
    sec_questions={
        "foodTypes": food_types,
        "mealType": meal_type,
        "veganOptions": vegan,
        "outdoor": outdoor,
        "locationType": restaurant_type,


    }

    return sec_questions

async def call_break(loc_restr,break_type,budget,day,hour):

    sorted_places=[]
    iters=0
    while not sorted_places and iters<4:
        iters+=1
        places=await break_alg(loc_restr,break_type,budget)
        all_places = [place for places in places.values() for place in places]


        sorted_places = sorted(all_places, key=lambda x: x["Q"])[:6]
        sorted_places = [
        place for place in sorted_places
        if is_open(place, day, hour,offset=2)
    ]
        loc_restr.circle.radius+=0.2
        break_type="default"

    if not sorted_places:
        raise Exception()
    best_place = min(sorted_places, key=lambda x: x["distance"])
    return best_place

    
        
async def break_alg(loc_restr,break_type,budget):
    loop=asyncio.get_running_loop()
    type = [
        {
      "key": break_type,
      **CATEGORY_CONFIG_RELAX[break_type]
    }
        
    ]

    raw_data=await fetch_places(type,loc_restr,EXTRA_RELAX)

    helpers_enrich = [
    solve_photos,
    ]
    enriched_data = await enrich_all(raw_data,ENRICHED_RELAX, helpers_enrich,CATEGORY_CONFIG_RELAX)

    ratios=[0.5,0.2,0.3]
    criteria_classification=["+","-","+"]
    needs_normalization=[False,True,False]
    helpers_score=[
        
        
        partial(rating_score,condition=3.6,z=1.4),
                   partial(dist,userLat=loc_restr.circle.center.latitude,userLong=loc_restr.circle.center.longitude,condition=2800,radius=loc_restr.circle.radius,ratio=1.5),
                   partial(price_score,budget=budget,sigma=0.45),
                   ]
    
    for type,places in enriched_data.items():
        loc_score_results = await loop.run_in_executor(
            DEFAULT_THREAD_POOL,
            compute_score,
            places,
            helpers_score,
            ratios,
            criteria_classification,
            needs_normalization,
            0.5,
            12,
            10
            
        )
        enriched_data[type]=loc_score_results

    return enriched_data

def calculate_walking_speed(place,intensity):
    speed_kmh=3.8+ 1.3*intensity
    distance=place.get("distance")*1.15
    time_minutes = (distance / (speed_kmh * 1000)) * 60
    return round(time_minutes, 1)

async def  best_food_place(init_loc_restr,food_types,meal_type,budget,day,hour,intensity):
    main_q_food={
        "distance":1+0.3*intensity,
        "budget":budget,
        "region":{
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude,
            "latitude_delta":0,
            "longitude_delta":0,
        },
        "category":"food",

    }

    sec_q_food=create_food_sec_questions(food_types,meal_type)
    sec_q_food=SecondaryQuestions.model_validate(sec_q_food)
    main_q_food = MainQuestions.model_validate(main_q_food)

    sorted_food_places=[]
    food_places={}
    iters=0
    while not sorted_food_places and iters<5:
        print("sorted food lungime:", sorted_food_places)
        iters+=1
        print("salut din while")
        async for update in food_alg(main_q_food, sec_q_food):
                    
                

                if any(update.get("data",{}).values()):
                    food_places=update["data"]
                    break
        
        all_food_places = [place for places in food_places.values() for place in places]


        sorted_food_places = sorted(all_food_places, key=lambda x: x["Q"])[:6]
        print("lungime in interiorul while inainte de sort :",len(sorted_food_places))
        sorted_food_places = [
        place for place in sorted_food_places
        if is_open(place, day, hour,offset=2)
    ]
        

        main_q_food.distance += 0.2 
        if "default" not in sec_q_food.foodTypes:
            sec_q_food.foodTypes.append("default")
    
    if not sorted_food_places:
        raise Exception()
    best_food_place = min(sorted_food_places, key=lambda x: x["distance"])


    return best_food_place





def is_open(place, day, hour,offset=2):
    min_open_time = hour
    min_close_time = hour + offset
    print("ora este :",hour)
    # ajustare dacă ora depășește 24
    if min_close_time >= 24:
        min_close_time -= 24
        next_day = (day + 1) % 7
    else:
        next_day = day

    oh = place.get("openingHours", {})
    if not oh:
        return False

    periods = oh.get("periods", [])
    if not periods:
        return False

    for period in periods:
        open_info = period.get("open", {})
        close_info = period.get("close", {})

        open_day = open_info.get("day", None)
        close_day = close_info.get("day", None)
        open_hour = open_info.get("hour", 0)
        close_hour = close_info.get("hour", 0)

        if open_day == close_day:
            if day == open_day and open_hour <= min_open_time and close_hour >= min_close_time:
                return True
        else:
            # overnight
            if (day == open_day and open_hour <= min_open_time) or \
               (day == next_day and close_hour >= min_close_time):
                return True
    print("am eliminat in is open")
    return False

def get_new_restriction(place,radius=1000):
    latitude = place.get("latitude")
    longitude = place.get("longitude")
    return location_restriction(latitude,longitude,distance=radius)
    

async def best_experience_cultural(init_loc_restr,type_of_activity,type_cultural,budget,day,hour,intensity_activities,intensity):
    
        
    cultural = random.random() < type_of_activity
    alg=None
    main_q = {
            "distance": 1 + 0.3 * intensity,
            "budget": budget,
            "region": {
                "latitude": init_loc_restr.circle.center.latitude,
                "longitude": init_loc_restr.circle.center.longitude,
                "latitude_delta": 0,
                "longitude_delta": 0,
            },
            "category": "",
        }
    if cultural:
        alg= history_alg
        main_q["category"] = "cultural"
        
        sec_q={
            "experienceType": type_cultural,
            "locationTypes": ["Muzee","Galerii de arta","Monumente","Arhitectura"]
            
        }

    else:
        alg=experience_alg
        main_q["category"] = "experiences"
        
        sec_q={
            
            "indoorOutdoor":"ambele",
            "physical": intensity_activities,
            
        }

    main_q = MainQuestions.model_validate(main_q)
    sec_q = SecondaryQuestions.model_validate(sec_q)
   
    all_places=[]
    iters=0
    while not all_places and iters<3:
        async for update in alg(main_q, sec_q,max_places=12,min_places=10,nearby_excluded_types=["movie_theatre"]):
            if any(update.get("data", {}).values()):
                places_ec = update["data"]
                break

        all_places = [place for places in places_ec.values() for place in places]
        sorted_places = sorted(all_places, key=lambda x: x["Q"])[:8]
        sorted_places = [
        place for place in sorted_places
        if is_open(place, day, hour)]
        
        main_q.distance += 0.2 

    best_place = min(sorted_places, key=lambda x: x["distance"])
    best_place["place_type_cat"]="cultural" if cultural else "experience"
    return best_place



async def best_shopping(budget,intensity,init_loc_restr,shopping_categories,day,hour):
    main_q = {
            "distance": 1 + 0.3 * intensity,
            "budget": budget,
            "region": {
                "latitude": init_loc_restr.circle.center.latitude,
                "longitude": init_loc_restr.circle.center.longitude,
                "latitude_delta": 0,
                "longitude_delta": 0,
            },
            "category": "shopping",
        }
   
    seq_q={
        "shoppingExperience": random.random(),
        "shoppingLocType":shopping_categories

    }

    main_q = MainQuestions.model_validate(main_q)
    sec_q = SecondaryQuestions.model_validate(seq_q)
    sorted_places=[]
    places_ec={}
    async for update in shopping_alg(main_q, sec_q):
        if any(update.get("data", {}).values()):
            places_ec = update["data"]
            break

    
        all_places = [place for places in places_ec.values() for place in places]
        sorted_places = sorted(all_places, key=lambda x: x["Q"])[:8]
        sorted_food_places = [
        place for place in sorted_food_places
        if is_open(place, day, hour)]

        main_q.distance += 0.2

        if "default" not in sec_q.shoppingLocType:
            sec_q.shoppingLocType.append("default")

    best_place = min(sorted_places, key=lambda x: x["distance"])

    return best_place

async def experience_enday(init_loc_restr,type_of_activity,type_cultural,budget,day,hour,intensity_activities,intensity):
    pass