import asyncio
import datetime
import random
from fapi.schemas import Circle,LocationRestriction,Center
from fapi.helpers.itinerary_helpers import first_period
from dateutil import parser
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
    await first_period(day,budget, loc_restr, food_types, type_of_activity, intesity_activities, type_cultural, shopping, shopping_categories, intensity)

    yield {
        "stage": "final",
        "data": []
    }
    






