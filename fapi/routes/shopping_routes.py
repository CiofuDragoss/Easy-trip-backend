from pprint import pprint
from fastapi import APIRouter,Depends,HTTPException,Query,status,Request,WebSocket,WebSocketDisconnect
from fapi.schemas import NearbySearch, ShoppingRequest,Circle,Center,LocationRestriction,TextSearch,Shopping,MainQuestions
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.constants.category_config import SHOPPING_CATEGORY_CONFIG
from fapi.routes.google_routes import google_nearby_search,google_text_search,google_details
from fapi.fapi_config import settings
from fapi.rec_algs.shopping_alg import shopping_alg #,night_life_alg,history_alg,food_alg,drinks_alg,experiences_alg
from fapi.helpers.bd_rec_save import save_recs,get_recs
import json
router=APIRouter()

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
        shop_q = Shopping.model_validate(payload["SecondaryQuestions"])
        print("Main Questions: ", main_q)
        print("Secondary Questions: ", shop_q)
        async for update in shopping_alg(main_q, shop_q):
                
            await websocket.send_json(update)

            if update.get("data",""):
                await save_recs(auth, update["data"],type)
                recs=await get_recs(auth)
                obj = recs[1]

                # dict-ul propriu-zis:
                data_dict = obj.data  # adaptează dacă are alt nume câmpului

                # îl dump-ezi în JSON:
                pprint(data_dict,sort_dicts=False)
                

                
        

    except WebSocketDisconnect or Exception:
        print("Client deconectat")
        return
    
        
    
      
    
    
    
    
        

    
    








    


