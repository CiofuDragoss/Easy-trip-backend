from beanie import Document
from pydantic import EmailStr
from pymongo.operations import IndexModel

class User(Document):
    username: str
    name:str
    email:EmailStr
    password:str
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True)
        ]