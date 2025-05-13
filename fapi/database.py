from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import User, JwtTokens,Recommendation
from .fapi_config import settings



async def init_db():
    
    client=AsyncIOMotorClient(settings.mongo)

    db=client[settings.db_name]
    await init_beanie(database=db, document_models=[User,JwtTokens, Recommendation])
