import asyncio
import datetime
import random
async def itinerary_alg(main_questions, sec_q):
    
    loop = asyncio.get_running_loop()
    distance=main_questions.distance*1000
    budget= main_questions.budget
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    itinerary_type=sec_q.itineraryType
    type_of_activity=sec_q.typeOfActivity
    type_cultural=sec_q.typeCultural
    intesity_activities=sec_q.intesityActivities
    shopping=sec_q.shopping
    wantsBreak=sec_q.breakk
    break_day_time=sec_q.breakDayTime
    break_type=sec_q.breakType
    shopping_categories=sec_q.shoppingCategories
    end_day=sec_q.endDayType
    intensity=sec_q.intensity
    

    yield {
        "stage": "final",
        "data": []
    }
    

def period_morning(circle,intensity,included=False):
    pass

def period_launch(circle,intensity,included=False):
    pass

def period_afternoon(circle,intensity,included=True):
    pass

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



