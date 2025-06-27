from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.fapi_config import settings
from fapi.schemas import NearbySearch, TextSearch, PlaceDetails
from fapi.constants.general_config import (
    NEARBY_SEARCH_URL,
    TEXT_SEARCH_URL,
    PLACE_DETAILS_URL,
    GOOGLE_WEATHER_URL,
    PHOTO_ENDPOINT,
)
import httpx
import asyncio
from fapi.constants.semaphores import SEMAPHORE_DETAILS, SEMAPHORE_PHOTOS
from pprint import pprint


async def init_multiplex_client_google():
    global http_client
    http_client = httpx.AsyncClient(
        http2=True,
        limits=httpx.Limits(max_keepalive_connections=100, max_connections=300),
        timeout=httpx.Timeout(10.0),
    )


async def shutdown_multiplex_client_google():
    await http_client.aclose()


router = APIRouter(dependencies=[Depends(verify_token_access)])


@router.post("/resolve_img_urls")
async def resolve_img_urls(photo_names: list[str]):
    tasks = [safe_google_photos(name) for name in photo_names]
    urls = await asyncio.gather(*tasks)
    urls = [url for url in urls if url is not None]
    return urls


async def reverse_geocode(lat, lng):
    params = {
        "latlng": f"{lat},{lng}",
        "key": settings.google_api,
        "result_type": "locality|country",
    }

    try:
        r = await http_client.get(settings.google_geocoding_api, params=params)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Eroare la Geocoding API: {exc}",
        )

    if r.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Geocoding API a rasp cu {r.status_code}: {r.text}",
        )

    data = r.json()
    if data.get("status") != "OK" or not data.get("results"):
        print(data)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nu am gasit rezultate pentru coordonate.",
        )

    city = None
    country = None

    for comp in data["results"][0]["address_components"]:
        types = comp.get("types", [])
        if "locality" in types:
            city = comp["long_name"]
        elif "country" in types:
            country = comp["long_name"]

    return {"city": city, "country": country}


async def get_weather(lat, long):
    params = {
        "key": settings.google_api,
        "location.latitude": lat,
        "location.longitude": long,
    }

    try:
        response = await http_client.get(GOOGLE_WEATHER_URL, params=params)
    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Eroare la trimiterea cererii către Google Weather API: {exc}",
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"Google Weather API a rasp cu {response.status_code}: "
                f"{response.text}"
            ),
        )
    resp_json = response.json()
    isDay = resp_json.get("isDaytime", None)
    temp = resp_json.get("temperature", {}).get("degrees")
    historyTemp = (
        resp_json.get("currentConditionsHistory", {})
        .get("maxTemperature", {})
        .get("degrees", "")
    )
    if isDay is None or not temp or not historyTemp:
        raise Exception()
    return {"temp": temp, "is_day": isDay, "max_temp": historyTemp}


async def google_nearby_search(request: NearbySearch):

    headers = {
        "X-Goog-FieldMask": ",".join(request.fieldMask) if request.fieldMask else None,
        "Content-Type": "application/json",
    }

    response = await http_client.post(
        NEARBY_SEARCH_URL,
        params={"key": settings.google_api},
        headers=headers,
        json=request.dict(exclude={"fieldMask"}, exclude_none=True),
    )
    data = response.json()
    return data


async def google_text_search(request: TextSearch):
    headers = {
        "X-Goog-FieldMask": ",".join(request.fieldMask) if request.fieldMask else None,
        "Content-Type": "application/json",
    }

    response = await http_client.post(
        TEXT_SEARCH_URL,
        params={"key": settings.google_api},
        headers=headers,
        json=request.model_dump(exclude={"fieldMask"}, exclude_none=True),
    )
    data = response.json()

    return data


async def google_details(placeId):

    url = f"{PLACE_DETAILS_URL}/{placeId}"
    headers = {"X-Goog-Api-Key": settings.google_api, "X-Goog-FieldMask": "types"}

    response = await http_client.get(url, headers=headers)
    data = response.json()

    return data


async def safe_google_details(place_id):

    return await google_details(place_id)


async def safe_google_photos(photo_name):

    response = await http_client.get(
        f"{PHOTO_ENDPOINT}{photo_name}/media",
        timeout=httpx.Timeout(20.0, read=20.0),
        params={
            "skipHttpRedirect": True,
            "key": settings.google_api,
            "maxWidthPx": 1000,
            "maxHeightPx": 1000,
        },
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("photoUri")
    else:
        return None
