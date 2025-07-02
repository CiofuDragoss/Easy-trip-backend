from beanie import Document, Link
from pydantic import EmailStr, Field
from pymongo.operations import IndexModel
from pymongo import ASCENDING, DESCENDING
from typing import Optional
import datetime


class User(Document):
    username: str
    email: EmailStr
    password: str

    class Settings:
        name = "users"
        indexes = [IndexModel([("email", 1)], unique=True)]


class Code(Document):
    email: EmailStr
    code: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    class Settings:
        name = "reset_codes"
        indexes = [
            IndexModel(
                [("created_at", ASCENDING)],
                expireAfterSeconds=15 * 60,
            ),
            IndexModel([("email", ASCENDING)], unique=True),
        ]


class VisitedPlaces(Document):
    user: Link[User]
    place_ids: list[str] = Field(default_factory=list)
    update_index: int = Field(default=0)

    class Settings:
        name = "visited_places"
        indexes = [IndexModel([("user", 1)], unique=True)]


class JwtTokens(Document):
    token: str
    user: Link[User]

    class Settings:
        name = "tokens"
        indexes = [IndexModel([("user", 1)], unique=True)]


class Recommendation(Document):
    user: Link[User]
    type: str = Field(default="recommendation")
    data: dict
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    location: Optional[str] = None

    class Settings:
        name = "recommendations"
        indexes = [
            IndexModel(
                [("created_at", ASCENDING)],
                expireAfterSeconds=7 * 24 * 3600,
            ),
            IndexModel(
                [("user", ASCENDING), ("created_at", DESCENDING)],
            ),
        ]


class BannedPlace(Document):
    place_id: str = Field(..., unique=True)

    ban_count: int = Field(default=0)
