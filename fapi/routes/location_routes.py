from fastapi import APIRouter,Depends,HTTPException,Query,status,Request
from fastapi.security import OAuth2PasswordBearer
import httpx
from fapi.schemas import AutocompleteRequest,PlaceDetails
from fapi.fapi_config import settings
from fapi.helpers.jwt_helpers import verify_token_access
router=APIRouter(dependencies=[Depends(verify_token_access)])
AUTOCOMPLETE_URL=settings.google_autocomplete_url
DETAILS_URL=settings.google_places_details
@router.get("/ip_location")
async def location_ip(publicIp: str):
    client_ip=publicIp
    async with httpx.AsyncClient() as client:
        response=await client.get(f"http://ip-api.com/json/{client_ip}")

    print(response.json())
    if response.status_code!=200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Eroare la comunicarea cu API")
    
    
    
    
    location=response.json()
    if location.get("status")=="fail":
        return  {'latitude': 45.9432,"longitude": 24.9668,"latitude_delta":4.7,"longitude_delta":9.5}
    else:
        return {'latitude': location.get("lat"),"longitude": location.get("lon"),"latitude_delta":0.1,"longitude_delta":0.1}

@router.post('/get_placeid_loc')
async def get_placeid_loc(
    req:PlaceDetails
):
    
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_api,
        "X-Goog-FieldMask": "location"
    }
    
    
    print("DETAILSLS", DETAILS_URL)
    async with httpx.AsyncClient() as client:
        response=await client.get(f"{DETAILS_URL}/{req.placeId}",headers=headers)
    print(response.json())
    if response.status_code !=200:
        raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Eroare la comunica cu Api-ul placeID google!"
        )
    
    place_loc=response.json()
    latitude = place_loc["location"]["latitude"]
    longitude = place_loc["location"]["longitude"]

    if not latitude or not longitude:
        return {}
    else:
        return {"latitude":latitude,"longitude":longitude,"latitude_delta":0.005,"longitude_delta":0.005}

@router.get("/location_autocomplete")
async def location_autocomplete(
    input:str=Query(...)
    
):
    body = {"input": input}
    
    headers = {
      "Content-Type": "application/json",
      "X-Goog-Api-Key": settings.google_api,
      "X-Goog-FieldMask":"suggestions.placePrediction.placeId,"
    "suggestions.placePrediction.structuredFormat"

    }
    print("AUTOO",AUTOCOMPLETE_URL)
    print("body", body)
    async with httpx.AsyncClient() as client:
        response=await client.post(AUTOCOMPLETE_URL,json=body,headers=headers)
    
    if response.status_code !=200:
        raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Eroare la comunica cu Api-ul de recomandari google!"
        )
    
    data=response.json()
    print(data)
    predictions = data.get("suggestions", [])
    print(predictions)
    results = []
    for prediction in predictions:
        sf = prediction["placePrediction"]
        sf_text=sf["structuredFormat"]
        main_text      = sf_text.get("mainText",{}).get("text","")
        secondary_text = sf_text.get("secondaryText",{}).get("text","")
        place_id       = sf["placeId"]
        results.append({
        "main_text":      main_text,
        "secondary_text": secondary_text,
        "place_id":       place_id,
        })
    
    return {"predictions": results}