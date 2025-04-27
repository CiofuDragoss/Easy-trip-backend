from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.fapi_config import settings
from fapi.schemas import NearbySearch, TextSearch, PlaceDetails
from fapi.constants.category_config import NEARBY_SEARCH_URL,TEXT_SEARCH_URL,PLACE_DETAILS_URL
import httpx
import asyncio

PHOTO_ENDPOINT = "https://places.googleapis.com/v1/places/photo"

async def resolve_img_urls(photo_names: list[str]):
    async with httpx.AsyncClient(follow_redirects=False) as client:
        tasks=[
            client.get(PHOTO_ENDPOINT,params={
                "photo":name,
                "key":settings.google_api
            })
            for name in photo_names
        ]
        responses = await asyncio.gather(*tasks)

        urls=[]        
        for resp in responses:
            if resp.status_code == 302 and "location" in resp.headers:
                urls.append(resp.headers["location"])
        else:
            
            urls.append(None)



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
        response=await client.post(TEXT_SEARCH_URL,params={"key": settings.google_api},headers=headers,json=request.dict(exclude={"fieldMask"}, exclude_none=True))
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
