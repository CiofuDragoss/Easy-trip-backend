from pydantic import BaseModel, EmailStr,Field,field_validator

class AuthIn(BaseModel):
    email:EmailStr
    password: str
   
class UserChecker(BaseModel):
    username:str
    name:str
    email: EmailStr
    password: str 
    

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    