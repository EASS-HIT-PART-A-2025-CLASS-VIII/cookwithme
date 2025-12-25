from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from sqlalchemy import Column, JSON


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
    rating: int = Field(ge=1, le=5)
    comment: str

    recipe: Optional["Recipe"] = Relationship(back_populates="reviews")


class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    ingredients: List[str] = Field(sa_column=Column(JSON))
    instructions_md: str
    time_minutes: int
    difficulty: Difficulty
    image_url: Optional[str] = None

    reviews: list[Review] = Relationship(back_populates="recipe")

class Highlight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    video_url: str
    cover_url: Optional[str] = None
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
    image_url: Optional[str] = None


class RecipeCreate(RecipeBase):
    pass


class RecipeRead(RecipeBase):
    id: int


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
