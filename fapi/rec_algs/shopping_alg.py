from fapi.helpers.math_helpers import gauss_score
import asyncio

from fapi.constants.shopping_config import CATEGORY_CONFIG, EXTRA, ENRICHED
from fapi.constants.executors import DEFAULT_THREAD_POOL
from fapi.schemas import LocationRestriction, Circle, Center
from fapi.routes.google_routes import (
    safe_google_details,
)
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
from functools import partial


# functie asincrona de tip generator, pentru comunicarea real-time catre client, prin ruta de web socket progresul.


async def shopping_alg(main_questions, secondary_questions, **kwargs):
    cancellation_event = kwargs.get("cancellation_event")
    max_places = kwargs.get("max_places", 9)
    min_places = kwargs.get("min_places", 8)
    loop = asyncio.get_running_loop()
    distance = int(main_questions.distance * 1000)
    budget = main_questions.budget
    type_cat = main_questions.category
    longitude = main_questions.region.longitude
    latitude = main_questions.region.latitude
    cat = secondary_questions.shoppingExperience
    local = secondary_questions.shoppingLocType
    # main questions si second questions vin de la utilizator si ne modeleaza rezultatele
    # conditii daca nu apelam din alg de itinerariu
    randomize = True if type_cat != "Itinerariu" else False

    dist_condition = 1000 if type_cat != "Itinerariu" else 50

    # restrictia de localizare pentru fetch places
    loc_restr = location_restriction(latitude, longitude, distance, randomize=randomize)
    types = [{"key": key.strip(), **CATEGORY_CONFIG[key.strip()]} for key in cat]

    # pentru helperi, in cazul in care o functie nu ia doar argumentul place, toate argumentele
    # externe la care enrich_all nu are acces, trebuie transmise din exterior.
    # folosim partial pentru a impacheta functia cu valorile argumentelor exterioare,in enrich_all, sau compute score,
    # i se adauga functiei doar valoarea argumentului "place"

    # helperi pentru enrich ,pentru adaugarea de atribute/modificare (solve photos)
    # observam ca ,deoarece getMallScore din helpers enriched este de forma getMallScore(place, keywords),trebuie impachetata cu
    # partial
    helpers_enrich = [partial(getMallScore, keywords=EXTRA.get("mall")), solve_photos]
    # helperii de scor care sunt apelati in compute score
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
        partial(price_score, budget=budget, sigma=0.4),
        partial(local_score, local=local, sigma=0.3),
    ]

    # ratio si classif. observam ca avem 4 helperi de scor, adica 4 criterii,adica 4 elemente in cele 2 liste.
    # observam ca distanta , cu cat este mai mica, cu atat este mai bine , deci  trebuie normalizata in cunostinta de cauza in vikor,
    # deci in classif avem "-"
    ratios = [0.3, 0.25, 0.15, 0.3]
    criteria_classification = ["+", "-", "+", "+"]
    # trimitem  update prin web socket catre utilizator
    yield {"stage": "pas 1", "info": "Cautam locatii din zona in care te afli..."}

    # datele initiale primite de la google prin logica fetch places
    raw_data = await fetch_places(
        types, loc_restr, EXTRA, cancellation_event=cancellation_event
    )
    # incepem pasii de enrich si score, deci nu mai avem mult, instiintam utilizatorul
    yield {"stage": "pas 2", "info": "pregatim locatiile si le filtram..."}
    # start enrich_all
    cleaned_data, banned_places = await enrich_all(
        raw_data,
        ENRICHED,
        helpers_enrich,
        CATEGORY_CONFIG,
        cancellation_event=cancellation_event,
    )
    # pentru fiecare categorie din CONFIG (in cazul nostru Moda si accesorii, Bijuterii etc.)
    # rulam compute score,la final obtinem lista finala , de tipul "Moda si accesorii":[date],
    # pentru afisare optima clientului
    for shopping_type, places in cleaned_data.items():
        if cancellation_event and cancellation_event.is_set():
            loc_score_results = []
            break
        # rulam in thread pentru a nu bloca serverul cu operatiile sincrone din compute_score
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
        cleaned_data[shopping_type] = loc_score_results
    # in final, trimitem catre client datele
    yield {"stage": "final", "data": cleaned_data}


# functie care imbogateste fiecare locatie in enrich, cu un indice inMall:0 sau 1
# avem nevoie de acest indice pentru calcularea scorului preferinta utilizatorului - tipul locatiei(daca se afla intr-un mall sau nu)
# functia este apelata iterativ de catre enrich all prin intermediul enrich, pentru fiecare locatie
async def getMallScore(place, keywords):
    display = place["display"]
    highlight = None
    # facem o verificare rudimentara,daca se afla anumite cuvinte in titlul locatiei inseamna ca este in mall
    inMall = 1 if any(kw.lower() in display.lower() for kw in keywords) else 0
    # inteorgam place_id_urile din containingPlaces a acelei locatii
    if inMall == 0 and place.get("containingPlaces"):
        tasks = [safe_google_details(p["id"]) for p in place["containingPlaces"]]
        for detail in await asyncio.gather(*tasks):
            # daca orice locatie din containingPlaces este de tip mall -> inMall=1
            if "shopping_mall" in detail.get("types", []):
                inMall = 1
                break
    # highlight pentru instiintarea utilizatorului
    if inMall:
        highlight = "Locatia se afla intr un mall."
    # structura oricarei functii de score sau inbogatire : return "nume",scor/valoare, highlight
    return "inMall", inMall, highlight


# scor local , daca locatia este stradala sau intr-un mall( atribut deja calculat in pasul de enrich), corelat prin
# gauss  la valoarea (intre 0 si 1) primita de la utilizator si obtinem cat de similare sunt, penalizand o abatere mare
# daca volorile sunt 1 si 0.5 , scorul va fi ~0.4 , nu 0.5 (liniar),si rasplatind o apropiere mai mare (daca valorile sunt 1 si 0.8)
# scorul va fi mai mare de 0.8
def local_score(place, local, condition=None, sigma=0.4):
    highlight = None
    # obtinem atributul calculat deja in pasul de imbogatire inMall
    inMall = place.get("inMall")
    localScore = gauss_score(inMall, local, sigma=sigma)
    return "localScore", round(localScore, 5), highlight
