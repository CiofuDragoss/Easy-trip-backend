from pprint import pprint
from fastapi import APIRouter,Depends,HTTPException,Query,status,Request,WebSocket,WebSocketDisconnect
from fapi.schemas import NearbySearch, ShoppingRequest,Circle,Center,LocationRestriction,TextSearch
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.constants.category_config import SHOPPING_CATEGORY_CONFIG
from fapi.routes.google_routes import google_nearby_search,google_text_search,google_details
from fapi.fapi_config import settings
from fapi.rec_algs.shopping_alg import shopping_alg #,night_life_alg,history_alg,food_alg,drinks_alg,experiences_alg


router=APIRouter()

@router.websocket("/ws/recommend")

async def Process_Request(websocket:WebSocket,token_data=Depends(verify_token_access)):
    

    await websocket.accept()

    try:
        payload=await websocket.receive_json()
        type=payload.get("type")
        main_q = payload.get("MainQuestions")
        shop_q = payload.get("ShoppingQuestions")
        async for update in shopping_alg(main_q, shop_q):
            await websocket.send_json(update)
        

    except WebSocketDisconnect:
        print("Client deconectat")
    finally:
        if not websocket.client_state.closed:
            await websocket.close()
    
        
    
      
    
    
    
    
        

    
    








    


