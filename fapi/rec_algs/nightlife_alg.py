import asyncio
from fapi.constants.executors import DEFAULT_THREAD_POOL, DEFAULT_PROCESS_POOL
from fapi.schemas import LocationRestriction, Circle, Center
from fapi.constants.nightlife_config import CATEGORY_CONFIG, EXTRA, ENRICHED
from fapi.constants.general_config import PRICE_LEVEL_MAP
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
from fapi.helpers.math_helpers import gauss_score
from functools import partial
from pprint import pprint
from dateutil import parser
from datetime import timedelta


async def nightlife_alg(main_questions, secondary_questions, **kwargs):
    cancellation_event = kwargs.get("cancellation_event")
    max_places = kwargs.get("max_places", 9)
    min_places = kwargs.get("min_places", 8)
    loop = asyncio.get_running_loop()
    distance = main_questions.distance * 1000
    budget = main_questions.budget
    type = main_questions.category
    longitude = main_questions.region.longitude
    latitude = main_questions.region.latitude
    atmosphere = secondary_questions.atmosphere
    date = parser.parse(secondary_questions.date)

    duration = int(secondary_questions.duration)
    location_types = secondary_questions.locationTypes
    randomize = True if type != "Itinerariu" else False

    dist_condition = 1000 if type != "Itinerariu" else 50
    loc_restr = location_restriction(latitude, longitude, distance, randomize=randomize)

    Types = [
        {"key": key.strip(), **CATEGORY_CONFIG[key.strip()]} for key in location_types
    ]

    yield {"stage": "pas 1", "info": "Cautam locatii din zona in care te afli..."}

    raw_data = await fetch_places(
        Types, loc_restr, EXTRA, cancellation_event=cancellation_event
    )

    yield {"stage": "pas 2", "info": "pregatim locatiile si le filtram..."}

    helpers_enrich = [
        enrich_live_music,
        athmosphere_enrich,
        solve_photos,
    ]
    ratios = [0.2, 0.15, 0.15, 0.15, 0.25, 0.1]
    criteria_classification = ["+", "-", "+", "+", "+", "+"]

    helpers_score = [
        partial(rating_score, condition=3.6, z=1.4),
        partial(
            dist,
            userLat=latitude,
            userLong=longitude,
            condition=dist_condition,
            radius=distance,
            ratio=1.5,
        ),
        partial(price_score, budget=budget, sigma=0.45),
        partial(athmosphere_score, athmosphere_input=atmosphere),
        partial(date_score, date=date, duration=duration),
        main_type_score,
    ]

    cleaned_data, banned_places = await enrich_all(
        raw_data,
        ENRICHED,
        helpers_enrich,
        CATEGORY_CONFIG,
        cancellation_event=cancellation_event,
    )

    for type, places in cleaned_data.items():
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
        cleaned_data[type] = loc_score_results

    yield {"stage": "final", "data": cleaned_data}


# imbogatim pentru a instiinta utilizatorul daca locatia ofera muzica live.
def enrich_live_music(place):
    highlight = None
    music = 0
    if place.get("liveMusic"):
        music = 1
        highlight = "Locatia ofera muzica live!"

    return "liveMusic", music, highlight


# imbogatim cu scorul intial de atmosfera a fiecarei locatii.
def athmosphere_enrich(place):
    athmosphere = 0
    highlight = None
    display = place.get("display")
    types = place.get("types")
    live_music = place.get("live_music")
    category = place.get("category")
    search_query = place.get("search_QUERY")
    if category == "Lounge" and search_query in ("night_club", "bar"):
        if not "lounge" in display.lower():

            raise Exception()

    if category == "Club de Noapte":
        if "night_club" in types:
            athmosphere = 1
            highlight = "Locatia asigura distractie si muzica pana se inchide!"
        else:
            athmosphere = 0.7

    elif category == "Lounge":
        athmosphere = 0.4
        if "night_club" in types:
            athmosphere = 0.7
    elif category == "Bar de noapte":

        if search_query == "bar":
            if "night_club" in types:
                athmosphere = 1
                highlight = "Locatia asigura distractie si muzica pana se inchide!"
            else:
                athmosphere = 0.35

        else:
            athmosphere = 0.75

    elif category == "Pub":
        if search_query == "night pub":
            athmosphere = 0.6
        else:
            athmosphere = 0.35
    elif category == "Karaoke":
        athmosphere = 0.6
        if "night_club" in types:
            athmosphere = 0.8
            highlight = "Locatia asigura distractie si muzica pana se inchide!"

    return "athmosphere", athmosphere, highlight


# scor atmosfera
def athmosphere_score(place, athmosphere_input):
    athmosphere = place.get("athmosphere")
    highlight = None
    athmosphere_s = gauss_score(athmosphere, athmosphere_input, sigma=0.3)
    return "atm_score", athmosphere_s, highlight


# scor tip
def main_type_score(place):

    p_type = place.get("primaryType")
    search_mode = place.get("search_mode") == "text_search"
    search_query = place.get("search_QUERY")
    cat = place.get("category")
    p_type_s = 0
    highlight = None
    if (
        cat in ["karaoke", "Club de Noapte"]
        and p_type == search_query
        and not search_mode
    ):
        p_type_s = 1
    if cat in ["karaoke", "Club de Noapte"] and search_mode:
        p_type_s = 0.7
    return "p_type_s", p_type_s, highlight


# scor data (cat din timpul pe care turistul doreste sa il petreaca in locatie este deschisa locatia respectiva)
def date_score(place, date, duration):

    oh = place.get("openingHours", {})
    if not oh:
        raise Exception("nu am opening_hours")
    periods = oh.get("periods", [])
    if not periods:
        raise Exception("nu am perioade")
    date_s = 0
    highlight = None
    end_datetime = date + timedelta(hours=duration)
    google_day_start = date.isoweekday() % 7
    week_sunday = (date - timedelta(days=google_day_start)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    total_seconds = duration * 3600
    covered_seconds = 0

    for period in periods:
        o = period.get("open", "")
        c = period.get("close", "")
        if not o:
            return "date_score", 0, None
        if not c:
            return "date_score", 1, "Locatia  este deschisa non-stop!"
        open_dt = week_sunday + timedelta(
            days=o["day"], hours=o["hour"], minutes=o["minute"]
        )
        close_dt = week_sunday + timedelta(
            days=c["day"], hours=c["hour"], minutes=c["minute"]
        )

        if close_dt <= open_dt:
            close_dt += timedelta(days=7)

        start_overlap = max(date, open_dt)
        end_overlap = min(end_datetime, close_dt)
        delta = (end_overlap - start_overlap).total_seconds()
        if delta > 0:
            covered_seconds += delta

    ratio = min(covered_seconds / total_seconds, 1.0)

    date_s = ratio

    if ratio == 1:
        highlight = (
            "Locatia  este deschisa pe toata perioada pe care doriti sa o petreceti!"
        )

    elif ratio == 0:
        highlight = "Locatia nu este deschisa pentru orele selectate de dumneavostra!"

    else:
        covered_hours = covered_seconds / 3600
        highlight = f"Locația este deschisă aproximativ {covered_hours:.1f} ore din cele {duration} ore cerute."
    return "date_score", date_s, highlight
