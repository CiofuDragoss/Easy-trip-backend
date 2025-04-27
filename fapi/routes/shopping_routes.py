from pprint import pprint
from fastapi import APIRouter,Depends,HTTPException,Query,status,Request
from fapi.schemas import NearbySearch, ShoppingRequest,Circle,Center,LocationRestriction,TextSearch
from fapi.helpers.jwt_helpers import verify_token_access
from fapi.constants.category_config import SHOPPING_CATEGORY_CONFIG
from fapi.routes.google_routes import google_nearby_search,google_text_search,google_details
from fapi.fapi_config import settings
from fapi.rec_algs.shopping_alg.py import shopping_alg


router=APIRouter(dependencies=[Depends(verify_token_access)])

@router.post("/shopping_questions")

async def Shopping_Request(request:ShoppingRequest):
    
    main_questions = request.MainQuestions
    shopping_questions = request.ShoppingQuestions

    try:
        # apelezi funcția și primești lista de rezultate
        results = await shopping_alg(main_questions, shopping_questions)
        
        # opțional, poți loga pentru debug:
        pprint(results)
        
        # și apoi returnezi JSON-ul
        return {"results": results}
    
    except Exception as e:
        # transformi orice eroare internă într-un HTTP 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shopping algorithm error: {e}"
        )
    
    
        

    
    








    


