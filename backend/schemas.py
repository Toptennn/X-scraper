from pydantic import BaseModel
from typing import Optional, Literal, List, Dict


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ScrapeRequest(BaseModel):
    x_auth_id: str
    x_password: str
    mode: Literal["timeline", "date_range", "popular", "latest"] = "timeline"
    screen_name: Optional[str]
    query: Optional[str]
    count: int = 50
    start_date: Optional[str]
    end_date: Optional[str]


class ScrapeResponse(BaseModel):
    tweets: List[Dict]
