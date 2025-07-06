import asyncio
import math
import pandas as pd
from fapi.constants.executors import DEFAULT_THREAD_POOL, DEFAULT_PROCESS_POOL
from fapi.helpers.math_helpers import wilson_score, gauss_score, haversine_distance
from fapi.schemas import LocationRestriction, Circle, Center, NearbySearch, TextSearch
from fapi.routes.google_routes import (
    safe_google_details,
    google_nearby_search,
    google_text_search,
)
import inspect
from functools import partial
from fapi.helpers.math_helpers import wilson_score, gauss_score, haversine_distance
from fapi.constants.general_config import PRICE_LEVEL_MAP

from fapi.helpers.bd_rec_save import filter_banned_places
import random


# obtinem din obiectul photos doar linkurile pentru transformat
def solve_photos(place):
    photos = place.get("photos", "")
    highlight = None
    if photos:
        photos = photos[:4]
        photo_names = [photo.get("name") for photo in photos if photo.get("name")]
        return "photos", photo_names, highlight
    raise Exception("conditie photos")


# obtinem rating score
def rating_score(place, condition=None, z=1.4):
    highlight = None
    rating = place.get("rating")
    if condition and rating < condition:
        raise Exception("conditie rating")
    ratingCount = place.get("ratingCount")
    ratingScore = wilson_score(rating, ratingCount, z)
    if ratingScore > 0.85:
        highlight = "Locatia aceasta are ratinguri excelente."

    return "ratingScore", round(ratingScore, 5), highlight


# returnam distanta , ca si score direct , vom folosi cu - in vikor ( cu cat este mai mica cu atat este mai buna)
def dist(place, userLat, userLong, radius, condition=10, ratio=1.5):
    highlight = None
    latitude = place.get("latitude")
    longitude = place.get("longitude")
    dist = haversine_distance(latitude, longitude, userLat, userLong)
    if dist < 1300:

        highlight = "Locatia este foarte aproape de dumneavostra!"
    if condition and (dist - radius) > condition:
        raise Exception("conditie dist")

    return "distance", dist, highlight


# pret score,initalizam cu 0.5 pentru ca de obicei nu avem priceLevel la locatii
def price_score(place, budget, condition=None, sigma=0.45):
    priceScore = 0.5
    highlight = None
    priceLevel = place.get("priceLevel")
    if priceLevel:
        price_level_value = PRICE_LEVEL_MAP[priceLevel]
        priceScore = gauss_score(price_level_value, budget, sigma=sigma)
        priceScore = round(priceScore, 5)
    return "priceScore", priceScore, highlight


# obtinem locatiile pe baza configurarii fiecarui algoritm
async def fetch_places(category, loc_restr, category_extra, cancellation_event=None):

    raw_data = []
    for category_type in category:
        # foarte important pentru a face cereri inutile in caz de anulare.
        if cancellation_event and cancellation_event.is_set():
            return raw_data
        entry = {
            "category_type": category_type["key"],
            "nearby_responses": [],
            "text_responses": [],
        }

        nearby_tasks = []
        text_tasks = []
        # iterram prin nearby type is nearby type non prim din category
        for t in category_type["nearby_type"]:
            req = NearbySearch(
                locationRestriction=loc_restr,
                excludedTypes=category_type["excludedTypes"].get(t, []),
                includedPrimaryTypes=[t],
                fieldMask=category_extra["Mask"],
            )

            nearby_tasks.append((google_nearby_search(req), t))

        for i in category_type.get("nearby_search_non_prim_types", []):
            req = NearbySearch(
                locationRestriction=loc_restr,
                excludedTypes=category_type["excludedTypes"].get(i, []),
                includedTypes=[i],
                fieldMask=category_extra["Mask"],
            )

            nearby_tasks.append((google_nearby_search(req), i))

        # iteram peste search text query
        for q in category_type["text_query"]:
            req = TextSearch(
                textQuery=q, locationBias=loc_restr, fieldMask=category_extra["Mask"]
            )
            text_tasks.append((google_text_search(req), q))
        # creem array-ul de taskuri si un array de key (search_query) din enrich, pentru ca este important, ne folosim de search_query
        # in mai multi algoritmi si situatii
        # output : search query -> [places]. daca avem nearby_type=["restaurant","fast_food_restaurant"] vom avea "reastaurant":[places]
        # "fast_food_restaurant"->[places]
        nearby_coros, nearby_keys = zip(*nearby_tasks) if nearby_tasks else ([], [])
        text_coros, text_keys = zip(*text_tasks) if text_tasks else ([], [])

        if cancellation_event and cancellation_event.is_set():
            return raw_data
        nearby_results = await asyncio.gather(*nearby_coros) if nearby_coros else []
        text_results = await asyncio.gather(*text_coros) if text_coros else []
        # run tasks
        for resp, t in zip(nearby_results, nearby_keys):

            entry["nearby_responses"].append(
                {"search_QUERY": t, "places": resp.get("places", [])}
            )

        for resp, q in zip(text_results, text_keys):
            entry["text_responses"].append(
                {"search_QUERY": q, "places": resp.get("places", [])}
            )
        # append category (entry)
        raw_data.append(entry)
    return raw_data


# helper pentru enrich, pentru a se potrivi cu formatul CONFIG pentru fiecare algoritm
def get_data(data, path, default=None):
    for key in path:

        data = data.get(key, default)
        if data is default:
            return default
    return data


# functie apelata de enrich all pentru fiecare place
# args-> functiile din helpers_enrich
# kwargs-> se adauga automat inainte de iterarea prin functii in obiectul nou creat
async def enrich_place(
    place, extract, category_type, search_type, cancellation_event, *args, **kwargs
):
    if cancellation_event and cancellation_event.is_set():
        return {}
    enriched = {}
    # highlights este un vector care este umplut fie in pasul de enrich( acum ) in cazul in care functiile
    # de enrch din args returneaza highlight,fie in pasul compute score de catre functiile de score
    enriched.update(
        {
            "category": category_type,
            "search_mode": search_type,
            "highlights": [],
            **kwargs,
        }
    )
    # iteram prin ENRICHED din config care ne defineste numele variabilelor noului obiect,
    # aici doar facem reasign si redenumire, curatare
    for var_name, (path_str, fallback) in extract.items():

        path = path_str.split(".")

        enriched[var_name] = get_data(place, path, fallback)
    # aici adaugam campuri noi pe baza structurii functiilor helper de enrich.daca functia este awaitable
    # o asteptam daca nu o rulam direct
    for fn in args:
        fn = partial(fn, enriched)
        result = fn()
        if inspect.isawaitable(result):
            var_name, value, highlight = await result
        else:
            var_name, value, highlight = result
        # daca avem highlight adaugam la vector
        if highlight:
            enriched["highlights"].append(highlight)

        enriched[var_name] = value

    """print("\n")
    print("types:",enriched.get("types",[]))
    print("primary type:",enriched.get("primaryType"))
    print("display name:",enriched.get("display"))"""
    # returnam noul obiect
    return enriched


# functie care verifica conform conditiilor din CONFIG un anumit place,inainte de a il trimite
# la imbogatire. se apeleaza in timpul rularii enrich_all
def verify_place(category_type, key, config, place, query):
    types = place.get("types", [])
    primary_type = place.get("primaryType")
    display = place.get("displayName", {}).get("text", "").lower()
    if key == "nearby_search":
        included = config[category_type].get("nearbyIncludedTypes").get(query, [])
        excludedPrimaryTypes = config[category_type].get(
            "nearbyExcludedPrimaryTypes", []
        )
        bannedWords = config[category_type]["bannedWordsNearby"]
        if not any(t in included for t in types) and included:
            return False

        if excludedPrimaryTypes and primary_type in excludedPrimaryTypes:
            return False
        if any(t in display for t in bannedWords) and bannedWords:
            return False

    else:
        included = config[category_type]["textIncludedTypes"]
        excluded = config[category_type]["textExcludedTypes"]
        bannedWords = config[category_type]["bannedWordsText"]
        excludedPrimaryTypes = config[category_type].get("textExcludedPrimaryTypes", [])
        if not any(t in included for t in types) and included:
            # print("eliminare in text search de la included")
            return False
        if any(t in excluded for t in types) and excluded:
            # print("eliminare in text search de la excluded")
            return False
        if excludedPrimaryTypes and primary_type in excludedPrimaryTypes:
            return False
        if any(t in display for t in bannedWords) and bannedWords:
            # print("eliminare in text search de la banned words")
            return False

    return True


# functie care face lista de taskuri enriched o lanseaza si ne da setul de date raw curatat (datele provenite din fetch direct de la google)
async def enrich_all(raw_data, extract, extra_funcs, config, cancellation_event=None):
    enriched_places = {}

    placeId_set = set()
    for entry in raw_data:
        tasks = []

        category_type = entry["category_type"]
        # iteram prin obiectul raw de la fetch_places
        for key, responses in [
            ("nearby_search", entry["nearby_responses"]),
            ("text_search", entry["text_responses"]),
        ]:
            # iteram peste fiecare obiect
            for resp in responses:
                query = resp.get("search_QUERY", "")
                for place in resp.get("places", []):
                    place_id = place.get("id")

                    # daca verify_place este false sau daca place_id in placeId_set continuam ,nu il luam in considerare

                    if place_id in placeId_set:

                        continue

                    if not verify_place(category_type, key, config, place, query):

                        continue
                    # adaugam in in placeId_set si adaugam taskul pentru acel place intr-un vector
                    placeId_set.add(place_id)

                    tasks.append(
                        enrich_place(
                            place,
                            extract,
                            category_type,
                            key,
                            cancellation_event,
                            *extra_funcs,
                            search_QUERY=query,
                        )
                    )

        if cancellation_event and cancellation_event.is_set():
            return {}, None
        # lansam concurent taskurile
        enriched = await asyncio.gather(*tasks, return_exceptions=True)
        # daca un task returneaza exceptie (pentru ca functiile de enrich si cele de score, in cazul in care anumite conditii nu sunt)
        # indeplinite, spre exemplu ,daca ratingul unei locatii este mai mic decat 3.6 , arunca exceptii, ignoram rezultatul
        # acelui task.
        enriched_places[category_type] = [
            r for r in enriched if not isinstance(r, Exception)
        ]

    if cancellation_event and cancellation_event.is_set():
        return {}, None
    # adaugam in baza de date id-urile locatiilor care nu sunt deja aflate in colectia de BannedPlace,
    # si o returnam pentru a o folosi in compute score.
    # check filter_banned_places pentru explicatie
    banned_set = await filter_banned_places(placeId_set)
    return enriched_places, banned_set


# functia care pune scoruri , aplica VIKOR, si sorteaza locatiile
def compute_score(
    cleaned_data,
    helpers,
    ratios,
    criteria_classification,
    banned_places,
    cancellation_event=None,
    v=0.5,
    max_places=12,
    min_places=8,
):
    if not cleaned_data:
        return []
    # initializare de variabile
    loc_score_results = []
    final_cleaned_places = []
    for place in cleaned_data:
        if cancellation_event and cancellation_event.is_set():
            return []

        loc_scores = {}

        # skip in caz ca vreo functie de score arunca o exceptie
        skip = False
        # iteram peste clasif ratio si functiile de score.
        # classif-> pentru fiecare functie de score + sau - , + daca criteriul este beneficiu - altfel, conform
        # teoriei vikor

        # ratio-> ponderea acelui criteriu (score)
        for fn, ratio, classification in zip(helpers, ratios, criteria_classification):

            try:

                var_name, value, highlight = fn(place)

                if highlight:
                    place["highlights"].append(highlight)

            except Exception as e:

                skip = True
                break
            # adaugam valoarea obtinuta si valorile ratio si clasif in loc_scores
            loc_scores[var_name] = value
            loc_scores[var_name + "_ratio"] = ratio
            loc_scores[var_name + "_clasif"] = classification

        # conditii de ignorare
        if skip:
            continue

        if place.get("placeId") in banned_places:
            continue
        # adaugam si placeId-ul locului pentru identificare dupa ce aplicam vikor (vom recombina cu datele sale intiale)
        loc_scores["placeId"] = place.get("placeId")

        """print("\n")
        print("types:", place.get("types", []))
        print("place id:", place.get("placeId"))
        print("primary type:", place.get("primaryType"))
        print("display name:", place.get("display"))
        print("serch query:", place.get("search_QUERY"))
        print("category:", place.get("category"))
        print("dist", place.get("distance"))"""

        # adaugam locul (doar cu criterii si scoruri)
        loc_score_results.append(loc_scores)

    if not loc_score_results:

        return []

    # start VIKOR

    # creem un dataframe pandas pentru metodele de calcul pe care ni le ofera
    df = pd.DataFrame(loc_score_results)
    df.set_index("placeId", inplace=True)

    if df.empty:
        return []

    all_columns = list(df.columns)
    criteria = []
    if cancellation_event and cancellation_event.is_set():

        return []
    # aflam numele fiecarui criteriu ( scorul efectiv )
    for col in all_columns:
        if col.endswith("_ratio"):
            var_base = col[: -len("_ratio")]
            criteria.append(var_base)

    if cancellation_event and cancellation_event.is_set():

        return []
    # in cazul in care avem criterii fara variatie (breaks vikor) le eliminam (ex. ratingScore este 0.8 peste tot)
    varied = []
    for var in criteria:
        vals = df[var].astype(float)
        if vals.max() - vals.min() > 0:

            varied.append(var)
    # criteria acum contine doar criteriile cu variatie
    criteria = varied

    if cancellation_event and cancellation_event.is_set():

        return []
    # incepem calculele pentru fiecare criteriul
    for var in criteria:

        clasif = f"{var}_clasif"
        ratio = f"{var}_ratio"

        values = df[var].astype(float)
        fmin = values.min()
        fmax = values.max()

        span = fmax - fmin or 1.0
        # toate ratiourile sunt la fel pentru un anumit criteriu deci ne trebuie un singur element
        ratios = df[ratio].iloc[0]

        # pasul de normalizare din vikor

        if df[clasif].eq("-").any():

            df[var] = (fmax - values) / span

        else:

            df[var] = (values - fmin) / span

        values = df[var].astype(float)
        # calcularea distantei fata de ideal conform vikor
        f_ideal = values.max()
        f_anti_ideal = values.min()
        df[var] = ratios * (f_ideal - values) / (f_ideal - f_anti_ideal)

    # eliminam coloanele clasif si ratio deoarece nu mai avem nevoie de ele, distantele sunt calculate
    # pentru fiecare criteriu

    cols_to_remove = [
        col for col in all_columns if col.endswith("_clasif") or col.endswith("_ratio")
    ]

    df.drop(columns=cols_to_remove, inplace=True)
    if cancellation_event and cancellation_event.is_set():

        return []
    # calcul S si R conform vikor
    df["S"] = df[criteria].sum(axis=1)
    df["R"] = df[criteria].max(axis=1)

    S_star = df["S"].min()
    S_minus = df["S"].max()
    R_star = df["R"].min()
    R_minus = df["R"].max()

    # nu mai avem nevoie de coloanele cu criterii (care acum sunt distantele)
    # din moment ce am calculat S si R
    df.drop(columns=criteria, inplace=True)
    # calculul Q , pasul final vikor (cu cat este mai mic cu atat este mai bun)
    df["Q"] = v * (df["S"] - S_star) / (S_minus - S_star) + (1 - v) * (
        df["R"] - R_star
    ) / (R_minus - R_star)

    # pentru siguranta , sa nu avem nan pe undeva (valoare care nu se poate transmite prin json)
    df["S"] = df["S"].fillna(0)
    df["R"] = df["R"].fillna(0)
    df["Q"] = df["Q"].fillna(0)

    # mapa pentru identificarea locatiilor procesate de vikor placeId: {scores Vikor}
    vikor_map = df.to_dict(orient="index")

    # END VIKOR
    # mapa pentru identificare locatiilor din loc_score_results, o facem pentru
    # a avea totusi in locatiile finale si valorile scorurilor initiale
    score_map = {
        entry["placeId"]: {
            k: v
            for k, v in entry.items()
            if k != "placeId" and not k.endswith(("_norm", "_ratio", "_clasif"))
        }
        for entry in loc_score_results
    }

    if cancellation_event and cancellation_event.is_set():

        return []
    # imbinarea datelor intiale despre o locatie din enriched, a scorurilor din vikor (S,R,Q) si a scorurilor intiale
    for place in cleaned_data:
        id = place.get("placeId")

        scores = score_map.get(id, None)
        vikor_vars = vikor_map.get(id, None)
        final_place = {}

        if scores is not None and vikor_vars is not None:
            final_place = {**place, **scores, **vikor_vars}

            final_cleaned_places.append(final_place)

    # vikor nu poate lucra cu o singura locatie neavand variatie, dar totusi pentru afisare in
    # client si evitarea valorilor nan ,avem nevoie de niste valori fictive pentru Q R si S

    if len(final_cleaned_places) == 1:

        final_cleaned_places[0]["Q"] = 1
        final_cleaned_places[0]["R"] = 1
        final_cleaned_places[0]["S"] = 1
        return final_cleaned_places

    if cancellation_event and cancellation_event.is_set():

        return []

    # sortarea pe baza Q (crescator)
    final_cleaned_places.sort(key=lambda x: x["Q"])

    # cuttof, 50% din locatii sau o valoare predefinita
    # valoarea hardocata 5 poate fi modificata dupa preferinte si performantele implementarii listei
    # de afisare din client
    n = len(final_cleaned_places)
    cutoff = math.ceil(n * 0.5) if 5 < math.ceil(n * 0.5) < max_places else min_places
    top_locations = final_cleaned_places[:cutoff]

    return top_locations


# helper pentru definirea restrictiei de locatie pentru cereri catre Google API
# randomize pentru o mica variatie a rezultatelor in caz ca avem recomandari obisnuite


def location_restriction(latitude, longitude, distance=1200, randomize=False):
    circle = Circle(
        center=Center(latitude=latitude, longitude=longitude),
        radius=(
            int(distance)
            if not randomize
            else int(distance)
            + int(random.uniform(-distance * 1 / 10, distance * 1 / 10))
        ),
    )
    loc_restr = LocationRestriction(circle=circle)

    return loc_restr
