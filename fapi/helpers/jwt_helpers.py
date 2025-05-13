from fastapi.security import OAuth2PasswordBearer
import jwt
import datetime
from fapi.models import JwtTokens 
from fastapi import HTTPException, status, Depends
from fapi.fapi_config import settings
oauth2_scheme_access = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_refresh = OAuth2PasswordBearer(tokenUrl="/auth/refresh")
def create_jwt_t(email:str,refresh:bool=False)->str:
    expire=int((datetime.datetime.now() + datetime.timedelta(minutes= settings.refresh_token_expire_minutes if refresh else  settings.access_token_expire_minutes)).timestamp())
    print("expira la: ", expire)
    payload={"sub":email,"exp":expire}
    print("payload ", payload)
    print("returnam : ",jwt.encode(payload,settings.secret_key_refresh if refresh else settings.secret_key,algorithm=settings.algorithm))
    return jwt.encode(payload,settings.secret_key_refresh if refresh else settings.secret_key,algorithm=settings.algorithm)

def verify_token_access(token:str=Depends(oauth2_scheme_access))->dict:
    try:
        
        payload=jwt.decode(token,settings.secret_key,algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tokenul a expirat",
            headers={"WWW-Authenticate":"Bearer"}
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tokenul este invalid",
            headers={"WWW-Authenticate":"Bearer"}
        )
    

async def verify_token_refresh(token:str=Depends(oauth2_scheme_refresh))->dict:
    try:
        payload=jwt.decode(token,settings.secret_key_refresh,algorithms=[settings.algorithm])
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tokenul a expirat",
            headers={"WWW-Authenticate":"Bearer"}
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tokenul este invalid",
            headers={"WWW-Authenticate":"Bearer"}
        )
    
    record = await JwtTokens.find_one(JwtTokens.token == token)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh token nerecunoscut sau revocat",
            )
    await record.fetch_link(JwtTokens.user)

    user_id = record.user.id
    return {"email": payload["sub"], "user": user_id}

