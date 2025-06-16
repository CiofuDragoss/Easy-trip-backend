from pydantic import BaseModel, EmailStr,ConfigDict


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
    