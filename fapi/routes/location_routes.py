from fastapi import APIRouter,Depends,HTTPException,Query,status,Request
from fastapi.security import OAuth2PasswordBearer
import httpx
from fapi.fapi_config import settings
from fapi.helpers.jwt_helpers import verify_token
from fapi.fapi_config import settings
router=APIRouter()

@router.get("/ip_location")
async def location_ip(request: Request,
    token_data:dict=Depends(verify_token)):
    client_ip=request.client.host
    print("salllll")
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
        return {'latitude': location.get("lat"),"longitude": location.get("lon"),"latitude_delta":0.005,"longitude_delta":0.005}

@router.get('/get_placeid_loc')
async def get_placeid_loc(
    query:str=Query(...),
    token_data:dict=Depends(verify_token)
):
    print("sall")
    google_url=settings.google_places_details
    params={
        "place_id":query,
        "key":settings.google_api
    }

    async with httpx.AsyncClient() as client:
        response=await client.get(google_url,params=params)

    if response.status_code !=200:
        raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Eroare la comunica cu Api-ul placeID google!"
        )
    
    place_loc=response.json()
    latitude=place_loc.get("result",{}).get("geometry",{}).get("location",{}).get("lat")
    longitude=place_loc.get("result",{}).get("geometry",{}).get("location",{}).get("lng")

    if not latitude or not longitude:
        return {}
    else:
        return {"latitude":latitude,"longitude":longitude,"latitude_delta":0.005,"longitude_delta":0.005}

@router.get("/location_autocomplete")
async def location_autocomplete(
    query:str=Query(...),
    token_data:dict=Depends(verify_token)
):

    google_url=settings.google_autocomplete_url
    params={
        "input":query,
        "key":settings.google_api
    }
    async with httpx.AsyncClient() as client:
        response=await client.get(google_url,params=params)
    
    if response.status_code !=200:
        raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Eroare la comunica cu Api-ul de recomandari google!"
        )
    
    data=response.json()
    predictions = data.get("predictions", [])
    print(predictions)
    results = []
    for prediction in predictions:
        print(prediction)
        sf = prediction.get("structured_formatting", {})
        main_text = sf.get("main_text", "")
        secondary_text = sf.get("secondary_text", "")
        place_id = prediction.get("place_id", "") 
        results.append({"main_text": main_text, "secondary_text": secondary_text,"place_id": place_id})
    
    return {"predictions": results}