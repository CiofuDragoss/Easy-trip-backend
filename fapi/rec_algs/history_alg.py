import asyncio
from fapi.constants.executors import DEFAULT_THREAD_POOL,DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction,Circle,Center



def history_alg(main_questions,shopping_questions):
    loop = asyncio.get_running_loop()
    loop = asyncio.get_running_loop()
    distance=main_questions.distance*1000
    budget= main_questions.budget
    local=shopping_questions.shoppingLocType
    longitude= main_questions.region.longitude
    latitude= main_questions.region.latitude
    
    circle=Circle(
        center=Center(
            latitude=latitude,
            longitude=longitude
        ),
        radius=distance
    )
    loc_restr = LocationRestriction(circle=circle)

    