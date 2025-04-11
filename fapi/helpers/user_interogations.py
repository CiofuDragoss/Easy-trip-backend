
from fapi.models import User
from fapi.schemas import UserChecker
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException,status
async def create_user(user_data:dict):
    try:
        user=User(**user_data)
        await user.insert()
        return {"email": user.email}
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Adresa de email este inregistrata deja! Logheaza-te!"
        )
async def get_user_by_email(email:str):
    user= await User.find_one(User.email==email)
    return user

