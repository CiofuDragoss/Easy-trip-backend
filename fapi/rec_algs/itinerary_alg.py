import asyncio
import datetime
import random
from fapi.schemas import Circle,LocationRestriction,Center
from fapi.helpers.itinerary_helpers import first_period
from dateutil import parser
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
    
    shopping_first = random.choices([True, False], k=1)[0] if itinerary_type=="Dimineata" and shopping else False
    shopping_second = not shopping_first if shopping else False
    included_first=True if itinerary_type=="Dimineata" else False
    result_first_period = await first_period(
        day=day,
        budget=budget,
        init_loc_restr=loc_restr,
        food_types=food_types,
        type_of_activity=type_of_activity,
        intensity_activities=intensity_activities,
        type_cultural=type_cultural,
        shopping=True,
        shopping_categories=shopping_categories,
        intensity=intensity,
        wants_break=wants_break,
        break_type=break_type,
        break_day_time=break_day_time,
        included=included_first
    )

    yield {
        "stage": "final",
        "data": result_first_period
    }
    






