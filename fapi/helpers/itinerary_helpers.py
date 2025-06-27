import random
from datetime import datetime
from fapi.rec_algs.food_alg import food_alg
from fapi.rec_algs.shopping_alg import shopping_alg
from fapi.rec_algs.history_alg import history_alg
from fapi.rec_algs.experience_alg import experience_alg
from fapi.helpers.alg_helpers import (
    fetch_places,
    enrich_all,
    compute_score,
    price_score,
    dist,
    rating_score,
    solve_photos,
    location_restriction,
)
from fapi.rec_algs.nightlife_alg import nightlife_alg
from fapi.constants.general_config import PRICE_LEVEL_MAP
from fapi.constants.executors import DEFAULT_THREAD_POOL
from fapi.schemas import (
    LocationRestriction,
    Circle,
    Center,
    SecondaryQuestions,
    MainQuestions,
)
from datetime import date, datetime, timedelta
from contextlib import suppress
import copy
import asyncio
from fapi.constants.Itinerary_config import (
    CATEGORY_CONFIG_RELAX,
    EXTRA_RELAX,
    ENRICHED_RELAX,
)
from functools import partial


async def first_period(
    day,
    budget,
    init_loc_restr,
    food_types,
    type_of_activity,
    intensity_activities,
    type_cultural,
    shopping,
    shopping_categories,
    intensity,
    wants_break,
    break_type,
    break_day_time,
    itinerary_type,
    global_set,
    included=False,
    cancellation_event=None,
):
    print("shopping estee:", shopping)
    print("tipe cultural:", type_cultural)
    excluded_types = ["movie_theater"]

    local_set = global_set
    cat_set = set()
    if not included:
        return {}, 14, init_loc_restr, cat_set
    final_first_period = {}
    time = 280
    start_hour = 9
    food_place, start_hour = await best_food_place(
        init_loc_restr,
        food_types,
        "Mic-dejun",
        budget,
        day,
        start_hour,
        intensity,
        local_set,
        cancellation_event,
    )
    local_set.add(food_place.get("placeId"))
    duration_walk = calculate_walking_speed(food_place, intensity)
    activity_duration = 45 - 15 * intensity
    final_first_period[
        f"Incepeti ziua cu micul dejun la {food_place.get('display')}.Aveti de mers {duration_walk} de la locatia dumneavostra.{"Parcurgeti traseul in ordine, altfel riscati sa mergeti mult intre locatii" if itinerary_type=="Dimineata" else ""}"
    ] = [food_place]
    time -= activity_duration + duration_walk
    start_hour += round((activity_duration + duration_walk) / 60)

    init_loc_restr = get_new_restriction(food_place)
    time, start_hour, init_loc_restr = await shopping_cultural_experience_loop(
        time,
        start_hour,
        init_loc_restr,
        wants_break,
        shopping,
        break_day_time,
        break_type,
        budget,
        day,
        local_set,
        cat_set,
        intensity,
        final_first_period,
        shopping_categories,
        type_of_activity,
        intensity_activities,
        type_cultural,
        excluded_types,
        cancellation_event,
        first_period=True,
    )
    return final_first_period, start_hour, init_loc_restr, cat_set


async def second_period(
    day,
    budget,
    init_loc_restr,
    food_types,
    type_of_activity,
    intensity_activities,
    type_cultural,
    shopping,
    shopping_categories,
    intensity,
    wants_break,
    break_type,
    break_day_time,
    end_day,
    start_hour,
    itinerary_type,
    global_set,
    cat_set,
    cancellation_event=None,
):
    excluded_types = ["movie_theater"]
    type_of_activity -= type_of_activity * (4 / 10)
    excluded_types_end_day = [
        "hiking_area",
        "ski_resort",
        "beach",
        "zoo",
        "water_park",
        "adventure_sports_center",
    ]
    local_set = global_set
    final_second_period = {}
    time = 360
    food_place, start_hour = await best_food_place(
        init_loc_restr,
        food_types,
        "Pranz",
        budget,
        day,
        start_hour,
        intensity,
        local_set,
        cancellation_event,
    )
    local_set.add(food_place.get("placeId"))
    duration_walk = calculate_walking_speed(food_place, intensity)
    activity_duration = 60 - 15 * intensity
    final_second_period[
        f"Luati pranzul la {food_place.get('display')}.Aveti de mers aproximativ {duration_walk} minute pana la restaurant.{"Parcurgeti traseul in ordine, altfel riscati sa mergeti mult de la o locatie la alta!" if itinerary_type=="Dupa masa" else ""}"
    ] = [food_place]
    time -= activity_duration + duration_walk
    start_hour += round((activity_duration + duration_walk) / 60)
    time, start_hour, init_loc_restr = await shopping_cultural_experience_loop(
        time,
        start_hour,
        init_loc_restr,
        wants_break,
        shopping,
        break_day_time,
        break_type,
        budget,
        day,
        local_set,
        cat_set,
        intensity,
        final_second_period,
        shopping_categories,
        type_of_activity,
        intensity_activities,
        type_cultural,
        excluded_types,
        cancellation_event,
    )

    food_place_dinner, start_hour = await best_food_place(
        init_loc_restr,
        food_types,
        "Cina",
        budget,
        day,
        start_hour,
        intensity,
        local_set,
        cancellation_event,
    )
    local_set.add(food_place_dinner.get("placeId"))
    duration_walk = calculate_walking_speed(food_place_dinner, intensity)
    final_second_period[
        f"Luati cina la {food_place_dinner.get('display')}. Aveti de mers aproximativ {duration_walk} minute pana la restaurant."
    ] = [food_place_dinner]
    start_hour += round((activity_duration + duration_walk) / 60)

    end_day_place = await best_end_day(
        init_loc_restr,
        end_day,
        budget,
        day,
        23,
        intensity,
        local_set,
        excluded_types_end_day,
        cancellation_event,
    )
    local_set.add(end_day_place.get("placeId"))
    duration_walk = calculate_walking_speed(end_day_place, intensity)

    final_second_period[
        f"Incheiati ziua la {end_day_place.get('display')}. Aveti de mers aproximativ {duration_walk} minute pana la locatie. Distractie placuta!"
    ] = [end_day_place]

    return final_second_period


async def shopping_cultural_experience_loop(
    time,
    start_hour,
    init_loc_restr,
    wants_break,
    shopping,
    break_day_time,
    break_type,
    budget,
    day,
    local_set,
    cat_set,
    intensity,
    final_second_period,
    shopping_categories,
    type_of_activity,
    intensity_activities,
    type_cultural,
    excluded_types,
    cancellation_event,
    first_period=False,
):
    first_activ = False
    while time > 0:
        if cancellation_event and cancellation_event.is_set():
            return []
        print("ora de inceput:", start_hour)

        if first_activ and wants_break and break_day_time == "Dupa masa":
            break_place = await call_break(
                init_loc_restr,
                break_type,
                budget,
                day,
                start_hour,
                local_set,
                cancellation_event,
            )
            local_set.add(break_place.get("placeId"))
            duration_walk = calculate_walking_speed(break_place, intensity)
            activity_duration = 50 - 20 * intensity
            time -= activity_duration + duration_walk
            start_hour += round((activity_duration + duration_walk) / 60)
            init_loc_restr = get_new_restriction(break_place)
            final_second_period[
                f"Faceti o pauza  la {break_place.get('display')}. Dureaza aproximativ {duration_walk} minute sa ajungeti."
            ] = [break_place]
            wants_break = False

            continue
        if first_activ and shopping:
            print("sunt la SHOPPINGGG")
            shopping_place = await best_shopping(
                budget,
                intensity,
                init_loc_restr,
                shopping_categories,
                day,
                start_hour,
                local_set,
                cancellation_event,
            )
            local_set.add(shopping_place.get("placeId"))
            duration_walk = calculate_walking_speed(shopping_place, intensity)
            activity_duration = 50 - 20 * intensity
            time -= activity_duration + duration_walk
            start_hour += round((activity_duration + duration_walk) / 60)
            init_loc_restr = get_new_restriction(shopping_place)
            final_second_period[
                f"Veti gasi cele mai bune produse din categoria {shopping_place.get('category')} la {shopping_place.get('display')}.Dureaza {duration_walk} sa ajungeti."
            ] = [shopping_place]
            shopping = False
            continue
        activity_place = await best_experience_cultural(
            init_loc_restr,
            type_of_activity,
            type_cultural,
            budget,
            day,
            start_hour,
            intensity_activities,
            intensity,
            local_set,
            cat_set,
            excluded_types,
            cancellation_event,
        )
        local_set.add(activity_place.get("placeId"))
        cat_set.add(activity_place.get("search_QUERY"))
        duration_walk = calculate_walking_speed(activity_place, intensity)
        activity_duration = (
            activity_place.get("duration", 70)
            - (activity_place.get("duration", 70) * 1 / 10) * intensity
            if activity_place.get("place_type_cat") == "experience"
            else 65 - 25 * intensity
        )
        time -= activity_duration + duration_walk
        start_hour += round((activity_duration + duration_walk) / 60)
        init_loc_restr = get_new_restriction(activity_place)
        if not first_activ:
            key = (
                f"Dupa ce terminati de luat {'micul dejun' if first_period else 'pranzul'}, vizitati {activity_place.get('display')}, veti invata multe si veti avea parte de o experienta culturala de neuitat.Dureaza {duration_walk} minute sa ajungeti."
                if activity_place.get("place_type_cat") == "cultural"
                else f"Dupa ce terminati de servit pranzul, incepeti programul cu o experienta placuta la {activity_place.get('display')}.Dureaza aproximativ {duration_walk} minute sa ajungeti."
            )
        else:
            key = (
                f"Continuati programul vizitand {activity_place.get('display')}.Bucurati-va de experienta culturala oferita de locatie.Dureaza {duration_walk} minute sa ajungeti."
                if activity_place.get("place_type_cat") == "cultural"
                else f"Continuati programul cu o experienta placuta la {activity_place.get('display')}.Dureaza aproximativ {duration_walk} minute sa ajungeti."
            )
        final_second_period[key] = [activity_place]

        first_activ = True
    return time, start_hour, init_loc_restr


def create_food_sec_questions(food_types, meal_type):
    now = datetime.now()
    seed = int(now.timestamp())
    random.seed(seed)

    vegan = 0
    outdoor = 1
    restaurant_type = random.uniform(0.55, 1)
    sec_questions = {
        "foodTypes": food_types,
        "mealType": meal_type,
        "veganOptions": vegan,
        "outdoor": outdoor,
        "locationType": restaurant_type,
    }

    return sec_questions


def check_hour_and_set_places(places, places_set, day, hour):
    all_places = [place for places in places.values() for place in places]

    sorted_places = sorted(all_places, key=lambda x: x["Q"])

    sorted_places = [
        place for place in sorted_places if is_open(place, day, hour, offset=2)
    ]

    check_set(sorted_places, places_set)

    return sorted_places


async def call_break(
    loc_restr, break_type, budget, day, hour, places_set, cancellation_event
):
    loc_restr_copy = copy.deepcopy(loc_restr)
    sorted_places = []
    iters = 0
    while not sorted_places and iters < 5:
        if cancellation_event and cancellation_event.is_set():
            return []
        iters += 1
        places = await break_alg(loc_restr_copy, break_type, budget, cancellation_event)
        sorted_places = check_hour_and_set_places(places, places_set, day, hour)
        loc_restr_copy.circle.radius += 200 * iters
        if break_type != "default" and iters > 2:
            break_type = "default"

    if not sorted_places:
        raise Exception()
    best_place = min(sorted_places, key=lambda x: x["distance"])
    return best_place


async def break_alg(loc_restr, break_type, budget, cancellation_event):
    loop = asyncio.get_running_loop()

    type = [{"key": break_type, **CATEGORY_CONFIG_RELAX[break_type]}]

    raw_data = await fetch_places(
        type, loc_restr, EXTRA_RELAX, cancellation_event=cancellation_event
    )

    helpers_enrich = [
        solve_photos,
    ]
    enriched_data = await enrich_all(
        raw_data,
        ENRICHED_RELAX,
        helpers_enrich,
        CATEGORY_CONFIG_RELAX,
        cancellation_event=cancellation_event,
    )

    ratios = [0.5, 0.2, 0.3]
    criteria_classification = ["+", "-", "+"]

    helpers_score = [
        partial(rating_score, condition=3.6, z=1.4),
        partial(
            dist,
            userLat=loc_restr.circle.center.latitude,
            userLong=loc_restr.circle.center.longitude,
            condition=10,
            radius=loc_restr.circle.radius,
            ratio=1.5,
        ),
        partial(price_score, budget=budget, sigma=0.45),
    ]
    if cancellation_event and cancellation_event.is_set():
        return []
    for type, places in enriched_data.items():
        if cancellation_event and cancellation_event.is_set():

            loc_score_results = []
            break
        loc_score_results = await loop.run_in_executor(
            DEFAULT_THREAD_POOL,
            compute_score,
            places,
            helpers_score,
            ratios,
            criteria_classification,
            cancellation_event,
            0.5,
            12,
            10,
        )
        enriched_data[type] = loc_score_results

    return enriched_data


def calculate_walking_speed(place, intensity):
    speed_kmh = 3.9 + 1.3 * max(intensity, 0.1)
    distance = place.get("distance") * 1.2
    time_minutes = (distance / (speed_kmh * 1000)) * 60
    return round(time_minutes, 1)


async def best_food_place(
    init_loc_restr,
    food_types,
    meal_type,
    budget,
    day,
    hour,
    intensity,
    places_set,
    cancellation_event,
):
    main_q_food = {
        "distance": 1 + 0.3 * intensity,
        "budget": budget,
        "region": {
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude,
            "latitude_delta": 0,
            "longitude_delta": 0,
        },
        "category": "Itinerariu",
    }

    sec_q_food = create_food_sec_questions(food_types, meal_type)
    sec_q_food = SecondaryQuestions.model_validate(sec_q_food)
    main_q_food = MainQuestions.model_validate(main_q_food)

    sorted_food_places = []
    food_places = {}
    iters = 0
    while not sorted_food_places and iters < 5:
        iters += 1
        print("iteratia:", iters)
        if cancellation_event and cancellation_event.is_set():
            return {}
        alg_gen = food_alg(
            main_q_food, sec_q_food, cancellation_event=cancellation_event
        )
        try:
            async for update in alg_gen:
                if cancellation_event and cancellation_event.is_set():
                    print("sunt aiciii in food")
                    break
                if any(update.get("data", {}).values()):
                    food_places = update["data"]
                    break
        finally:
            with suppress(Exception):
                await alg_gen.aclose()

        sorted_food_places = check_hour_and_set_places(
            food_places, places_set, day, hour
        )
        if not sorted_food_places and hour == 9:
            hour += 1
        main_q_food.distance += 0.2 * iters
        if "default" not in sec_q_food.foodTypes and iters > 2:
            sec_q_food.foodTypes.append("default")

    if not sorted_food_places:
        raise Exception()
    best_food_place = min(sorted_food_places, key=lambda x: x["distance"])
    return best_food_place, hour


def is_open(place, day, hour, offset=2):
    min_open_time = hour
    min_close_time = hour + offset
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

    for i, period in enumerate(periods, start=1):
        open_info = period.get("open", {})
        close_info = period.get("close", {})
        open_day = open_info.get("day")
        close_day = close_info.get("day")
        open_hour = open_info.get("hour", 0)
        close_hour = close_info.get("hour", 0)
        if close_day is None:
            return True

        if open_day == close_day:

            if (
                day == open_day
                and open_hour <= min_open_time
                and close_hour >= min_close_time
            ):

                return True
        else:

            cond1 = day == open_day and open_hour <= min_open_time
            cond2 = day == next_day and close_hour >= min_close_time

            if cond1 or cond2:

                return True

    return False


def get_new_restriction(place, radius=1000):
    latitude = place.get("latitude")
    longitude = place.get("longitude")
    return location_restriction(latitude, longitude, distance=int(radius))


async def best_experience_cultural(
    init_loc_restr,
    type_of_activity,
    type_cultural,
    budget,
    day,
    hour,
    intensity_activities,
    intensity,
    places_set,
    cat_set,
    excluded_types,
    cancellation_event,
):

    cultural = random.random() < type_of_activity
    alg = None
    main_q = {
        "distance": 1 + 0.3 * intensity,
        "budget": budget,
        "region": {
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude,
            "latitude_delta": 0,
            "longitude_delta": 0,
        },
        "category": "Itinerariu",
    }
    if cultural:
        alg = history_alg
        main_q["category"] = "cultural"

        sec_q = {
            "experienceType": type_cultural,
            "locationTypes": ["Muzee", "Galerii de arta", "Monumente", "Arhitectura"],
        }

    else:
        alg = experience_alg
        main_q["category"] = "experiences"

        sec_q = {
            "indoorOutdoor": random.choice(["ambele", "indoor", "outdoor"]),
            "physical": intensity_activities,
        }

    main_q = MainQuestions.model_validate(main_q)
    sec_q = SecondaryQuestions.model_validate(sec_q)
    places_ec = {}
    sorted_places = []
    iters = 0

    while not sorted_places and iters < 5:
        if cancellation_event and cancellation_event.is_set():
            return {}
        iters += 1
        alg_gen = alg(
            main_q,
            sec_q,
            max_places=12,
            min_places=10,
            nearby_excluded_types=excluded_types,
            cancellation_event=cancellation_event,
        )
        try:
            async for update in alg_gen:
                if cancellation_event and cancellation_event.is_set():
                    break
                if any(update.get("data", {}).values()):
                    places_ec = update["data"]
                    break
        finally:

            with suppress(Exception):
                await alg_gen.aclose()

        sorted_places = check_hour_and_set_places(places_ec, places_set, day, hour)

        if not cultural:
            s_p_copy = copy.deepcopy(sorted_places)
            check_set(s_p_copy, cat_set, get_str="search_QUERY")
            if len(s_p_copy) > 0:
                sorted_places = copy.deepcopy(s_p_copy)
            if iters > 2:
                sec_q.indoorOutdoor = "ambele"
        main_q.distance += 0.3 * iters
        print("lungime sorted places dupa final bucla experience:", len(sorted_places))
    best_place = min(sorted_places, key=lambda x: x["distance"])
    best_place["place_type_cat"] = "cultural" if cultural else "experience"
    return best_place


async def best_shopping(
    budget,
    intensity,
    init_loc_restr,
    shopping_categories,
    day,
    hour,
    places_set,
    cancellation_event,
):
    main_q = {
        "distance": 1 + 0.3 * intensity,
        "budget": budget,
        "region": {
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude,
            "latitude_delta": 0,
            "longitude_delta": 0,
        },
        "category": "Itinerariu",
    }

    seq_q = {
        "shoppingExperience": shopping_categories,
        "shoppingLocType": random.random(),
    }

    main_q = MainQuestions.model_validate(main_q)
    sec_q = SecondaryQuestions.model_validate(seq_q)
    sorted_places = []
    places_ec = {}
    iters = 0

    while not sorted_places and iters < 5:
        iters += 1
        if cancellation_event and cancellation_event.is_set():
            return {}
        alg_gen = shopping_alg(main_q, sec_q, cancellation_event=cancellation_event)
        try:
            async for update in alg_gen:
                if cancellation_event and cancellation_event.is_set():
                    break
                if any(update.get("data", {}).values()):
                    places_ec = update["data"]
                    break
        finally:
            with suppress(Exception):
                await alg_gen.aclose()

            sorted_places = check_hour_and_set_places(places_ec, places_set, day, hour)
            main_q.distance += 0.2 * iters

            if "default" not in sec_q.shoppingExperience:
                sec_q.shoppingExperience.append("default")

    best_place = min(sorted_places, key=lambda x: x["distance"])
    return best_place


def check_set(place_list, places_set, get_str="placeId"):
    place_list[:] = [
        place for place in place_list if place.get(get_str) not in places_set
    ]


async def best_end_day(
    init_loc_restr,
    type_of_enday,
    budget,
    day,
    hour,
    intensity,
    places_set,
    excluded_types,
    cancellation_event,
):

    alg = None
    main_q = {
        "distance": 1 + 0.3 * intensity,
        "budget": budget,
        "region": {
            "latitude": init_loc_restr.circle.center.latitude,
            "longitude": init_loc_restr.circle.center.longitude,
            "latitude_delta": 0,
            "longitude_delta": 0,
        },
        "category": "Itinerariu",
    }
    if type_of_enday == "Muzica si distractie":
        alg = nightlife_alg

        google_day = day
        python_wday = (google_day + 6) % 7
        today = date.today()
        today_wday = today.weekday()
        days_ahead = (python_wday - today_wday) % 7
        target_date = today + timedelta(days=days_ahead)
        dt = datetime(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
            hour=hour,
            minute=0,
            second=0,
        )
        sec_q = {
            "atmosphere": 0.8,
            "date": dt.isoformat(),
            "duration": 4,
            "locationTypes": ["Bar de noapte", "Club de Noapte"],
        }

    else:
        alg = experience_alg
        sec_q = {
            "indoorOutdoor": "ambele",
            "physical": 0.2,
        }

    main_q = MainQuestions.model_validate(main_q)
    sec_q = SecondaryQuestions.model_validate(sec_q)

    sorted_places = []
    places_ec = {}
    iters = 0

    while not sorted_places and iters < 6:
        if cancellation_event and cancellation_event.is_set():
            return {}
        iters += 1
        alg_gen = alg(
            main_q,
            sec_q,
            max_places=12,
            min_places=10,
            nearby_excluded_types=excluded_types,
            cancellation_event=cancellation_event,
        )
        try:
            async for update in alg_gen:
                if cancellation_event and cancellation_event.is_set():
                    break
                if any(update.get("data", {}).values()):
                    places_ec = update["data"]
                    break
        finally:
            with suppress(Exception):
                await alg_gen.aclose()

        sorted_places = check_hour_and_set_places(places_ec, places_set, day, hour)
        if alg == nightlife_alg:

            sorted_places = [
                place for place in sorted_places if place.get("date_score", 0) >= 0.3
            ]
        if alg == nightlife_alg and iters > 2:
            sec_q.locationTypes + ["Lounge", "Pub"]
        main_q.distance += 0.2 * iters

        if alg == experience_alg and iters > 3:
            sec_q = sec_q = {
                "atmosphere": 0.3,
                "date": dt.isoformat(),
                "duration": 4,
                "locationTypes": ["Lounge", "Bar de noapte", "Pub"],
            }
            alg = nightlife_alg
    best_place = min(sorted_places, key=lambda x: x["distance"])
    return best_place
