from pprint import pprint
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Request,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from fapi.schemas import (
    SecondaryQuestions,
    MainQuestions,
)
from fapi.routes.google_routes import (
    reverse_geocode,
)
from fapi.fapi_config import settings
from fapi.rec_algs.shopping_alg import (
    shopping_alg,
)  # ,night_life_alg,history_alg,food_alg,drinks_alg,experiences_alg
from fapi.rec_algs.history_alg import history_alg
from fapi.rec_algs.experience_alg import experience_alg
from fapi.rec_algs.drinks_alg import drinks_alg
from fapi.rec_algs.food_alg import food_alg
from fapi.helpers.bd_rec_save import save_recs
from fapi.rec_algs.nightlife_alg import nightlife_alg
from fapi.rec_algs.itinerary_alg import itinerary_alg
from contextlib import suppress
import asyncio
import threading
from pprint import pprint
from fastapi.encoders import jsonable_encoder

router = APIRouter()

ALG_MAP = {
    "Shopping": shopping_alg,
    "Istorie & Arta": history_alg,
    "Experiente": experience_alg,
    "Mancare": food_alg,
    "Bauturi": drinks_alg,
    "Viata de Noapte": nightlife_alg,
    "Itinerariu": itinerary_alg,
}


@router.websocket("/ws/recommend")
async def Process_Request(websocket: WebSocket):

    cancellation_event = threading.Event()
    await websocket.accept()

    auth = websocket.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    monitor_task = None

    async def connection_monitor():

        while True:
            if cancellation_event.is_set():
                return
            try:
                await asyncio.wait_for(
                    websocket.send_json({"type": "ping"}), timeout=20
                )
            except (asyncio.TimeoutError, WebSocketDisconnect):
                cancellation_event.set()
                return
            await asyncio.sleep(0.1)

    try:
        payload = await websocket.receive_json()
        main_q = MainQuestions.model_validate(payload["MainQuestions"])
        type_cat = main_q.category
        shop_q = SecondaryQuestions.model_validate(payload["SecondaryQuestions"])
        alg_function = ALG_MAP.get(type_cat)
        longitude = main_q.region.longitude
        latitude = main_q.region.latitude
        try:

            country_and_city = await reverse_geocode(latitude, longitude)
        except HTTPException:

            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="Probleme la server. Incercati din nou!",
            )

        location_for_bd = (
            f"{country_and_city.get('country','')}, {country_and_city.get('city','')}"
        )
        monitor_task = asyncio.create_task(connection_monitor())
        alg_gen = alg_function(
            main_q, shop_q, auth=auth, cancellation_event=cancellation_event
        )

        async for update in alg_gen:
            if cancellation_event.is_set():
                break

            if update.get("data", ""):

                data = jsonable_encoder(update["data"])
                if any(update.get("data", {}).values()):
                    await save_recs(auth, data, type_cat, location_for_bd)

            await websocket.send_json(jsonable_encoder(update))

            if update.get("data", ""):
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                await alg_gen.aclose()
                if monitor_task:
                    monitor_task.cancel()
                return

    except WebSocketDisconnect:
        cancellation_event.set()

    except Exception as e:
        print(e)
        raise WebSocketException(
            code=status.WS_1011_INTERNAL_ERROR,
            reason="Nu am reusit sa gasim suficiente locatii. Incercati o alta locatie initiala sau o raza de cautare mai mare.",
        )

    finally:
        if monitor_task:
            monitor_task.cancel()
        if not cancellation_event.is_set():
            cancellation_event.set()
        await asyncio.sleep(0.1)
        with suppress(Exception):
            await alg_gen.aclose()
