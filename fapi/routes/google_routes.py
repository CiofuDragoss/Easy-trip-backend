from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.fapi_config import settings
from fapi.schemas import NearbySearch, TextSearch, PlaceDetails
from fapi.constants.category_config import NEARBY_SEARCH_URL,TEXT_SEARCH_URL,PLACE_DETAILS_URL
import httpx
import asyncio
from fapi.constants.semaphores import SEMAPHORE_DETAILS,SEMAPHORE_PHOTOS
from pprint import pprint

PHOTO_ENDPOINT = "https://places.googleapis.com/v1/"

async def resolve_img_urls(photo_names: list[str]):
    tasks=[safe_google_photos(name) for name in photo_names]
    urls=await asyncio.gather(*tasks)
    urls=[url for url in urls if url is not None]
    return urls
            



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

    print("requesttt text search",request.dict(exclude={"fieldMask"}, exclude_none=True))
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
                        params={
                    "skipHttpRedirect": True,
                    "key": settings.google_api,    # your API key
                    "maxWidthPx": 400,             # note the string keys
                    "maxHeightPx": 400
                        }
               )
               if response.status_code == 200:
                data = response.json()
                return data.get("photoUri")
               else:
                return None
               
