from fastapi import APIRouter, HTTPException, status, Depends
import aiosmtplib
from email.message import EmailMessage
from fapi.helpers.auth_helpers import (
    send_verification_code_email,
    validate_code,
)
from fapi.schemas import (
    AuthIn,
    TokenOut,
    UserChecker,
    ResetPasswordRequest,
    CodeOnlyEmail,
)
from fapi.models import JwtTokens
from fapi.helpers.user_interogations import create_user, get_user_by_email
from fapi.helpers.hash_helpers import hash_pass, verify_pass
from fapi.helpers.jwt_helpers import create_jwt_t
from fapi.helpers.jwt_helpers import verify_token_access, verify_token_refresh
from pydantic import EmailStr
from fapi.models import User
from fapi.routes.user_and_bd_routes import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/verify_access")
async def check_access_token(token_data: dict = Depends(verify_token_access)):
    return token_data


@router.get("/refresh", response_model=TokenOut)
async def refresh_token(token_data: dict = Depends(verify_token_refresh)):
    email = token_data["email"]
    user_id = token_data["user"]
    new_refresh = create_jwt_t(email, refresh=True)
    new_access = create_jwt_t(email, refresh=False)
    print("asta e user id", user_id)
    await JwtTokens.get_motor_collection().update_one(
        {"user": user_id},
        {"$set": {"token": new_refresh}},
    )

    return TokenOut(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
    )


@router.post("/signup", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserChecker):

    user_dict = user_data.model_dump()
    user_dict["password"] = hash_pass(user_dict["password"])

    user = await create_user(user_dict)

    refresh_token = create_jwt_t(user.email, refresh=True)
    access_token = create_jwt_t(user.email, refresh=False)
    await JwtTokens(token=refresh_token, user=user.id).insert()
    return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenOut)
async def login(user_data: AuthIn):
    user = await get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nu exista un cont cu emailul {user_data.email}",
        )
    if not verify_pass(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Combinatie de email si parola invalida!",
        )

    refresh_token = create_jwt_t(user.email, refresh=True)
    access_token = create_jwt_t(user.email, refresh=False)
    await JwtTokens.get_motor_collection().update_one(
        {"user": user.id}, {"$set": {"token": refresh_token}}, upsert=True
    )
    return TokenOut(
        access_token=access_token, refresh_token=refresh_token, username=user.username
    )


@router.post("/send-reset-noUser")
async def send_reset_email(email: EmailStr):
    await send_verification_code_email(email)
    return {"msg": "Codul a fost trimis pe email."}


@router.post("/confirm-reset-pass-noUser")
async def confirm_code(data: ResetPasswordRequest):
    print("sunt aici")
    valid = await validate_code(data.email, data.code)
    if not valid:
        raise HTTPException(400, "Cod invalid sau expirat")

    user = await User.find_one(User.email == data.email)
    if not user:
        raise HTTPException(404, "Utilizatorul nu exista")
    if verify_pass(data.new_password, user.password):
        raise HTTPException(400, "Ati introdus parola veche!")
    user.password = hash_pass(data.new_password)
    await user.save()
    return {"msg": "Parola a fost resetata cu succes."}


@router.post("/verify-code")
async def verify_code_generic(data: CodeOnlyEmail):
    is_valid = await validate_code(data.email, data.code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Cod invalid sau expirat")
    return {"msg": "Codul este valid."}
