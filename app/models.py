from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from sqlalchemy import Column, JSON, func, DateTime
from pydantic import field_validator, BaseModel, EmailStr, Field as PydField
from datetime import datetime


# ---------------------------------------
# ENUMS
# ---------------------------------------
class Difficulty(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


# ---------------------------------------
# DB MODELS (TABLES)
# ---------------------------------------
class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    recipe_id: int = Field(foreign_key="recipe.id")
    user_id: int = Field(foreign_key="user.id")  

    rating: int = Field(ge=1, le=5)
    comment: str

    author_email: str = Field(default="", index=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    recipe: Optional["Recipe"] = Relationship(back_populates="reviews")
    user: Optional["User"] = Relationship()


class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    ingredients: List[str] = Field(sa_column=Column(JSON))
    instructions_md: str
    time_minutes: int
    difficulty: Difficulty
    image_url: Optional[str] = None

    reviews: List["Review"] = Relationship(back_populates="recipe")

class Highlight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    video_url: str
    cover_url: Optional[str] = None

class Favorite(SQLModel, table=True):
    __tablename__ = "favorite"
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", primary_key=True)
    created_at: Optional[datetime] = Field(default=None)

class RecipeView(SQLModel, table=True):
    __tablename__ = "recipe_view"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    recipe_id: int = Field(foreign_key="recipe.id", index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
# ---------------------------------------
# API MODELS (REQUEST / RESPONSE)
# ---------------------------------------
# בסיס למודלים API — ללא DB ID וללא קשרי DB
class RecipeBase(SQLModel):
    title: str
    ingredients: List[str]
    instructions_md: str
    time_minutes: int
    difficulty: Difficulty
    image_url: Optional[str] = ""

    @field_validator("title")
    @classmethod
    def title_length(cls, v):
        if len(v) < 2:
            raise ValueError("Title too short")
        return v

    @field_validator("time_minutes")
    @classmethod
    def positive_time(cls, v):
        if v <= 0:
            raise ValueError("Time must be positive")
        return v

    @field_validator("image_url")
    @classmethod
    def valid_image_url(cls, v):
        if len(v) < 5:
            raise ValueError("Image URL too short")
        return v


class RecipeCreate(RecipeBase):
    pass


class RecipeRead(RecipeBase):
    id: int

class RecipeReadWithStats(RecipeRead):
    avg_rating: float = 0.0
    reviews_count: int = 0

class RecipeUpdate(SQLModel):
    title: Optional[str] = None
    ingredients: Optional[List[str]] = None
    instructions_md: Optional[str] = None
    time_minutes: Optional[int] = None
    difficulty: Optional[Difficulty] = None
    image_url: Optional[str] = None


class ReviewCreate(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str


class ReviewRead(SQLModel):
    id: int
    rating: int
    comment: str

    user_id: int
    author_email: str
    created_at: Optional[datetime] = None
    
class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    name: str = Field(index=True) 
    role: UserRole = Field(default=UserRole.user)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = PydField(min_length=6, max_length=128)

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    class Config:
        from_attributes = True 

