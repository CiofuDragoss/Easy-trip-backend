from pprint import pprint
from fastapi import APIRouter,Depends,HTTPException,Query,status,Request,WebSocket,WebSocketDisconnect
from fapi.schemas import NearbySearch, ShoppingRequest,Circle,Center,LocationRestriction,TextSearch,SecondaryQuestions,MainQuestions
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.routes.google_routes import google_nearby_search,google_text_search,google_details
from fapi.fapi_config import settings
from fapi.rec_algs.shopping_alg import shopping_alg #,night_life_alg,history_alg,food_alg,drinks_alg,experiences_alg
from fapi.rec_algs.history_alg import history_alg
from fapi.rec_algs.experience_alg import experience_alg
from fapi.rec_algs.drinks_alg import drinks_alg
from fapi.rec_algs.food_alg import food_alg
from fapi.helpers.bd_rec_save import save_recs,get_recs
from fapi.rec_algs.nightlife_alg import nightlife_alg
from fapi.rec_algs.itinerary_alg import itinerary_alg
import json
from pprint import pprint
router=APIRouter()

ALG_MAP = {
    "Shopping": shopping_alg,
    "Istorie & Arta":  history_alg,
    "Experiente" : experience_alg,
    "Mancare":food_alg,
    "Bauturi":drinks_alg,
    "Viata de Noapte": nightlife_alg,
    "itinerary":itinerary_alg
}

@router.websocket("/ws/recommend")

async def Process_Request(websocket:WebSocket):
    
    
    await websocket.accept()

    auth= websocket.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload=await websocket.receive_json()
        main_q =  MainQuestions.model_validate(payload["MainQuestions"])
        type=main_q.category
        print("typee:", type)
        shop_q = SecondaryQuestions.model_validate(payload["SecondaryQuestions"])
        alg_function = ALG_MAP.get(type)
        
        async for update in alg_function(main_q, shop_q):
                
            

            if update.get("data",""):

                await save_recs(auth, update["data"],type)
                recs=await get_recs(auth)

                filtered_data = {}
                for category, places in update["data"].items():
                    filtered_places = []
                    for place in places:
                        # construiești un nou dict care să conțină TOT din place, 
                        # cu excepția cheilor "reviews" și "photos"
                        pr = {k: v for k, v in place.items() if k not in ("reviews", "photos","openingHours")}
                        filtered_places.append(pr)
                    filtered_data[category] = filtered_places

                # acum faci pprint pe filtered_data, fără să-ți mai apară reviews și photos:
                #pprint(filtered_data, sort_dicts=False)
                

            
            await websocket.send_json(update)

            if update.get("data",""):
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                return
        

                
                

                
        

    except WebSocketDisconnect or Exception as e:
        print(e)
        
        print("Client deconectat")
        return
    
        
    
      
    
    
    
    
        

    
    








    


