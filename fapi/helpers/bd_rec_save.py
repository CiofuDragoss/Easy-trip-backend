from fapi.helpers.jwt_helpers import verify_token_access
from beanie import Link
from fastapi import HTTPException, status
from fapi.models import User, Recommendation

async def save_recs(token,rec_data,type):
    token = token.split(" ")[1].strip()
    
    try:
        payload = verify_token_access(token)
    except Exception as e:
        raise Exception("Token invalid")
    
    email: str = payload.get("sub")

    user=await User.find_one(User.email == email)
    if not user:
        raise Exception("Nu Avem user")
    
    rec = Recommendation(
        type=type,
        user=user,
        data=rec_data
    )

    await rec.insert()


async def get_recs(token):
    token = token.split(" ")[1].strip()
    payload = verify_token_access(token)
    
    email: str = payload.get("sub")

    user=await User.find_one(User.email == email)
    if not user:
        raise Exception("Nu Avem user")
    
    recs = await Recommendation.find(Recommendation.user.id == user.id).to_list()
    
    return recs