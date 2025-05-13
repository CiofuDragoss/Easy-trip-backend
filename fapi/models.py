from beanie import Document,Link
from pydantic import EmailStr,Field
from pymongo.operations import IndexModel
from pymongo import ASCENDING, DESCENDING
import datetime
class User(Document):
    username: str
    email:EmailStr
    password:str
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True)
        ]

class JwtTokens(Document):
    token:str
    user:Link[User]
    class Settings:
        name = "tokens"
        indexes = [
            IndexModel([("user", 1)], unique=True)
        ]

class Recommendation(Document):
    user: Link[User]         
    type: str = Field(default="recommendation")
    data: dict
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    class Settings:
        name = "recommendations"
        IndexModel([("created_at", DESCENDING), ("user", ASCENDING)],
                   expireAfterSeconds=3 * 7 * 24 * 3600),