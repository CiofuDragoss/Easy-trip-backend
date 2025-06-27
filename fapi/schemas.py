from pydantic import BaseModel, EmailStr,ConfigDict,Field
from beanie import PydanticObjectId
from datetime import datetime
from typing import Optional,Literal
class SecondaryQuestions(BaseModel):
    model_config = ConfigDict(extra='allow')

class AuthIn(BaseModel):
    email:EmailStr
    password: str
   
class UserChecker(BaseModel):
    username:str
    email: EmailStr
    password: str 
    

class TokenOut(BaseModel):
    access_token: str
    refresh_token:str
    username:str=None
    token_type: str = "bearer"

class Region(BaseModel):
    latitude: float
    latitude_delta: float
    longitude: float
    longitude_delta: float
    
class Shopping(BaseModel):
    shoppingExperience: list[str]
    shoppingLocType:float

class MainQuestions(BaseModel):
    budget: float
    category:str
    distance:float
    region: Region

class RecommendationDetail(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id")
    type: str
    data: dict
    created_at: datetime
    location: Optional[str]

    model_config = ConfigDict(
        validate_by_name=True,
        
        json_encoders={PydanticObjectId: str},
    )


class RecommendationMeta(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id")
    type: str
    created_at: datetime
    location: Optional[str]

    model_config = ConfigDict(
        validate_by_name=True,
        json_encoders={PydanticObjectId: str},
    )

class ShoppingRequest(BaseModel):
    MainQuestions: MainQuestions
    ShoppingQuestions: Shopping
class Center(BaseModel):
    latitude:  float
    longitude: float

class Circle(BaseModel):
    center: Center
    radius: int

class LocationRestriction(BaseModel):
    circle: Circle


class AutocompleteRequest(BaseModel):
    input:str
    

class NearbySearch(BaseModel):
    locationRestriction:LocationRestriction
    includedTypes: list[str] = None
    includedPrimaryTypes:list[str]=None
    excludedTypes:list[str]=None
    maxResultCount:int = 20
    fieldMask: list[str] = ["places.displayName",
        "places.primaryType",
        "places.rating",
        "places.types",
        "places.containingPlaces",
        "places.userRatingCount",
        "places.priceLevel",
        ]
class TogglePayload(BaseModel):
    place_id: str
    add: bool
class TextSearch(BaseModel):
    textQuery: str
    locationBias:LocationRestriction
    languageCode:str="en"
    maxResultCount:int = 20
    fieldMask: list[str] = ["places.displayName",
        "places.primaryType",
        "places.types",
        "places.containingPlaces",
        "places.rating",
        "places.userRatingCount",
        "places.priceLevel",
        ]
    

class PlaceDetails(BaseModel):
    placeId: str
    