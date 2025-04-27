from beanie import Document,Link
from pydantic import EmailStr
from pymongo.operations import IndexModel

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