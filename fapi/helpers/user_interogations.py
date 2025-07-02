from fapi.models import User
from fapi.schemas import UserChecker
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException, status


# creaza user
async def create_user(user_data: dict) -> User:
    try:
        user = User(**user_data)
        await user.insert()
        return user
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Adresa de email este inregistrata deja! Logheaza-te!",
        )


async def get_user_by_email(email: str) -> User:
    user = await User.find_one(User.email == email)
    return user
