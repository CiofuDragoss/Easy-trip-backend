from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.fapi_config import settings
from fapi.schemas import NearbySearch, TextSearch, PlaceDetails
from fapi.constants.general_config import NEARBY_SEARCH_URL,TEXT_SEARCH_URL,PLACE_DETAILS_URL,GOOGLE_WEATHER_URL,PHOTO_ENDPOINT
import httpx
import asyncio
from fapi.constants.semaphores import SEMAPHORE_DETAILS,SEMAPHORE_PHOTOS
from pprint import pprint





router = APIRouter(dependencies=[Depends(verify_token_access)])
@router.post("/resolve_img_urls")
async def resolve_img_urls(photo_names: list[str]):
    tasks=[safe_google_photos(name) for name in photo_names]
    urls=await asyncio.gather(*tasks)
    urls=[url for url in urls if url is not None]
    print(urls)
    return urls

            

async def get_weather(lat,long):
    params = {
        "key": settings.google_api,      
        "location.latitude": lat,
        "location.longitude": long,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(GOOGLE_WEATHER_URL, params=params)
        except httpx.RequestError as exc:
               
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Eroare la trimiterea cererii către Google Weather API: {exc}"
                )

        if response.status_code != 200:
           
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    f"Google Weather API a răspuns cu {response.status_code}: "
                    f"{response.text}"
                )
            )
    resp_json=response.json()
    isDay=resp_json.get("isDaytime",None)
    temp=resp_json.get("temperature",{}).get("degrees")
    historyTemp=resp_json.get("currentConditionsHistory",{}).get("maxTemperature",{}).get("degrees","")
    if  isDay is None or not temp or not historyTemp:
        
        print("am ajuns aicii")
        raise Exception()
    return {
        "temp":temp,
        "is_day":isDay,
        "max_temp":historyTemp

    }



async def google_nearby_search(request:NearbySearch):
    
    headers={
        
        "X-Goog-FieldMask": ",".join(request.fieldMask) if request.fieldMask else None,
        "Content-Type":     "application/json",
    }
    print("requesttt",request.dict(exclude={"fieldMask"}, exclude_none=True))
    async with httpx.AsyncClient() as client:
        response=await client.post(NEARBY_SEARCH_URL,params={"key": settings.google_api},headers=headers,json=request.dict(exclude={"fieldMask"}, exclude_none=True))
        data=response.json()
    return data



async def google_text_search(request:TextSearch):
    headers={
        
        "X-Goog-FieldMask": ",".join(request.fieldMask) if request.fieldMask else None,
        "Content-Type":     "application/json",
    }

    print("requesttt text search",request.model_dump(exclude={"fieldMask"}, exclude_none=True))
    async with httpx.AsyncClient() as client:
        response=await client.post(TEXT_SEARCH_URL,params={"key": settings.google_api},headers=headers,json=request.model_dump(exclude={"fieldMask"}, exclude_none=True))
        data=response.json()

    return data


async def google_details(placeId):
    
     url=f"{PLACE_DETAILS_URL}/{placeId}"
     headers={
         "X-Goog-Api-Key":settings.google_api,
         "X-Goog-FieldMask":"types"
     }
    
     
     async with httpx.AsyncClient() as client:
         response=await client.get(url,headers=headers)
         data=response.json()

     
     
     return data

async def safe_google_details(place_id):
     async with SEMAPHORE_DETAILS:
          return await google_details(place_id)
     
async def safe_google_photos(photo_name):
     async with SEMAPHORE_PHOTOS:
          async with httpx.AsyncClient() as client:
               response=await client.get(f"{PHOTO_ENDPOINT}{photo_name}/media",
                                         timeout=httpx.Timeout(20.0, read=20.0),
                        params={
                    "skipHttpRedirect": True,
                    "key": settings.google_api,   
                    "maxWidthPx": 1000,             
                    "maxHeightPx": 1000
                        }
               )
               if response.status_code == 200:
                data = response.json()
                return data.get("photoUri")
               else:
                return None
               
