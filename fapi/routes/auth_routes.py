from fastapi import APIRouter, HTTPException, status,Depends

from fapi.schemas import AuthIn,TokenOut,UserChecker
from fapi.models import JwtTokens
from fapi.helpers.user_interogations import create_user,get_user_by_email
from fapi.helpers.hash_helpers import hash_pass,verify_pass
from fapi.helpers.jwt_helpers import create_jwt_t
from fapi.helpers.jwt_helpers import verify_token_access,verify_token_refresh

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.get("/verify_access")
async def check_access_token(token_data: dict = Depends(verify_token_access)):
    return token_data
@router.get("/refresh", response_model=TokenOut)
async def refresh_token(token_data:dict = Depends(verify_token_refresh)):
    email   = token_data["email"]
    user_id = token_data["user"]
    new_refresh = create_jwt_t(email, refresh=True)
    new_access  = create_jwt_t(email, refresh=False)
    print("asta e user id",user_id)
    result= await JwtTokens.get_motor_collection().update_one(
        { "user": user_id },                 
        { "$set": { "token": new_refresh }},        
    )
    
    return TokenOut(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
    )

@router.post("/signup", response_model=TokenOut, status_code= status.HTTP_201_CREATED)
async def signup(user_data: UserChecker):
    
    user_dict = user_data.model_dump()
    user_dict["password"] = hash_pass(user_dict["password"])

    user = await create_user(user_dict)

    refresh_token=create_jwt_t(user.email,refresh=True)
    access_token=create_jwt_t(user.email,refresh=False)
    await JwtTokens(token=refresh_token, user=user.id).insert()
    return TokenOut(access_token=access_token,refresh_token=refresh_token)
    
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Combinatie de email si parola invalida!"
        )
    
    

    
    refresh_token=create_jwt_t(user.email,refresh=True)
    access_token=create_jwt_t(user.email,refresh=False)
    await JwtTokens.get_motor_collection().update_one(
        {"user": user.id},              
        {"$set": {"token": refresh_token}},
        upsert=True                      
    )
    return TokenOut(access_token=access_token,refresh_token=refresh_token,username=user.username)