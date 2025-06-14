import random
import datetime
from fapi.rec_algs.food_alg import food_alg
from fapi.helpers.alg_helpers import fetch_places,enrich_all,compute_score,price_score,dist,rating_score,solve_photos
from fapi.constants.general_config import PRICE_LEVEL_MAP
async def first_period(budget,init_loc_restr,food_types,type_of_activity,intesity_activities, type_cultural,shopping, shopping_categories,itensity,included=False):
    main_q_food={
        "distance":900,
        "budget":budget,
        "region":{
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude
        }

    }

    sec_q_food=create_food_sec_questions(food_types,"Mic-dejun")

    food_places=await food_alg(main_q_food,sec_q_food,condition=10)



    time=240


async def second_period(budget,food_types,init_loc_restr,type_of_activity,intesity_activities, type_cultural,shopping, shopping_categories,break_day_time,break_type,wantsBreak,itensity,included=False):
    main_q_food={
        "distance":900,
        "budget":budget,
        "region":{
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude
        }

    }

    sec_q_food=create_food_sec_questions(food_types,"Pranz")

    food_places=await food_alg(main_q_food,sec_q_food,condition=10)

    all_food_places = [place for places in food_places.values() for place in places]

    sorted_food_places = sorted(all_food_places, key=lambda x: x["Q"])[:5]

    best_food_place = min(sorted_food_places, key=lambda x: x["distance"])

    time-=calculate_walking_speed(best_food_place)

    
    

async def last_period(budget,food_types,init_loc_restr,type_of_activity,intesity_activities, type_cultural,shopping, shopping_categories,break_day_time,break_type,wantsBreak,end_day,itensity,included=True):

    main_q_food={
        "distance":900,
        "budget":budget,
        "region":{
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude
        }

    }

    sec_q_food=create_food_sec_questions(food_types,"Cina",condition=10)

    food_places=await food_alg(main_q_food,sec_q_food)


def create_food_sec_questions(food_types,meal_type):
    now=datetime.now()
    seed = int(now.timestamp())
    random.seed(seed)
    
    vegan           = 0
    outdoor         = 1
    restaurant_type = random.uniform(0.45, 8)
    sec_questions={
        food_types: food_types,
        meal_type: meal_type,
        vegan: vegan,
        outdoor: outdoor,
        restaurant_type: restaurant_type,


    }


def experiences(init_loc_restr,intesity_activities):

    pass

def calculate_walking_speed(place,speed_kmh=4.5):
    distance=place.get("distance")*1.15
    time_minutes = (distance / (speed_kmh * 1000)) * 60
    return round(time_minutes, 1)