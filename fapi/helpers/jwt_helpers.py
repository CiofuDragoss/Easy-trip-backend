from fastapi.security import OAuth2PasswordBearer
import jwt
import datetime
from fastapi import HTTPException, status, Depends
from fapi.fapi_config import settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_jwt_t(email:str)->str:
    expire=int((datetime.datetime.now() + datetime.timedelta(minutes=settings.access_token_expire_minutes)).timestamp())
    print("expira la: ", expire)
    payload={"sub":email,"exp":expire}
    print("payload ", payload)
    print("returnam : ",jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm))
    return jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm)

def verify_token(token:str=Depends(oauth2_scheme))->dict:
    try:
        payload=jwt.decode(token,settings.secret_key,algorithms=settings.algorithm)
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
