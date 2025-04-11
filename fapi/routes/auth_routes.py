from fastapi import APIRouter, HTTPException, status
from fapi.schemas import AuthIn,TokenOut,UserChecker


from fapi.helpers.user_interogations import create_user,get_user_by_email
from fapi.helpers.hash_helpers import hash_pass,verify_pass
from fapi.helpers.jwt_helpers import create_jwt_t
router = APIRouter(prefix="/auth", tags=["Auth"])





@router.post("/signup", response_model=TokenOut, status_code= status.HTTP_201_CREATED)
async def signup(user_data: UserChecker):
    
    user_dict=user_data.model_dump()
    user_dict["password"]=hash_pass(user_dict["password"])
    email=await create_user(user_dict)
    token=create_jwt_t(email)
    return TokenOut(access_token=token)
    
@router.post("/login", response_model=TokenOut)
async def login(user_data: AuthIn):
    print("am primit: ")
    user=await get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nu exista un cont cu emailul {user_data.email}"
        )
    if not verify_pass(user_data.password,user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combinatie de email si parola invalida!"
        )
    token = create_jwt_t(user_data.email)
    return TokenOut(access_token=token)