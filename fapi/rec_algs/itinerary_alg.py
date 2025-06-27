import asyncio
import datetime
from pprint import pprint
import random
from fapi.schemas import Circle,LocationRestriction,Center
from fapi.helpers.itinerary_helpers import first_period,second_period
from dateutil import parser
from fapi.helpers.bd_rec_save import get_visited_set,add_to_visited
import random
import json
async def itinerary_alg(main_questions, sec_q,**kwargs):
    cancellation_event = kwargs.get("cancellation_event")
    auth=kwargs.get("auth","")
    if not auth:
        raise Exception("Probleme cu autentificarea!")
    loop = asyncio.get_running_loop()
    distance=main_questions.distance*1000
    budget= main_questions.budget
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    itinerary_type=sec_q.itineraryType
    type_of_activity=sec_q.typeOfActivity
    type_cultural=sec_q.typeCultural
    intensity_activities=sec_q.intesityActivities
    shopping=sec_q.shopping
    wants_break=sec_q.breakk
    break_day_time=sec_q.breakDayTime
    break_type=sec_q.breakType
    shopping_categories=sec_q.shoppingCategories
    end_day=sec_q.endDayType
    intensity=sec_q.intensity
    food_types=sec_q.foodTypes
    day=sec_q.day
    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=distance
    )
    loc_restr = LocationRestriction(circle=circle)
    yield{
            "stage": "pas 1",
            "info": "itinerariul tau se genereaza..."
        }
    visited_instance,global_set=await get_visited_set(auth)
    shopping_first = random.choice([True, False]) if itinerary_type=="Dimineata" and shopping else False
    shopping_second = not shopping_first if shopping else False
    included_first=True if itinerary_type=="Dimineata" else False
    result_first_period,start_hour,loc_restr,cat_set = await first_period(
        day=day,
        itinerary_type=itinerary_type,
        budget=budget,
        init_loc_restr=loc_restr,
        food_types=food_types,
        type_of_activity=type_of_activity,
        intensity_activities=intensity_activities,
        type_cultural=type_cultural,
        shopping=shopping_first,
        shopping_categories=shopping_categories,
        intensity=intensity,
        wants_break=wants_break,
        break_type=break_type,
        break_day_time=break_day_time,
        included=included_first,
        global_set=global_set,
        cancellation_event=cancellation_event,
    )
    yield{
            "stage": "pas 2",
            "info": "mai avem putin..."
        }
    await add_to_visited(visited_instance,global_set)
    result_second_period = await second_period(
    day=day,
    budget=budget,
    init_loc_restr=loc_restr,
    food_types=food_types,
    type_of_activity=type_of_activity,
    intensity_activities=intensity_activities,
    type_cultural=type_cultural,
    shopping=shopping_second,
    shopping_categories=shopping_categories,
    intensity=intensity,
    wants_break=wants_break,
    break_type=break_type,
    break_day_time=break_day_time,
    end_day=end_day,
    start_hour=start_hour,
    itinerary_type=itinerary_type,
    global_set=global_set,
    cat_set=cat_set,
    cancellation_event=cancellation_event
)
    await add_to_visited(visited_instance,global_set)
            
    yield {
        "stage": "final",
        "data": {**result_first_period,**result_second_period}
    }
    






