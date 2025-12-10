from sqlmodel import SQLModel, Field
from typing import Optional, List
from enum import Enum
from sqlalchemy import Column, JSON

class Difficulty(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class RecipeBase(SQLModel):
    title: str = Field(min_length=2)
    ingredients: List[str] = Field(
        sa_column=Column(JSON), ## Stores ingredients as JSON to keep the API clean and strongly typed
        description="List of ingredients"
    )
    instructions_md: str = Field(
    min_length=10,
    description="Markdown formatted cooking instructions"
    )
    time_minutes: int = Field(gt=0)
    difficulty: Difficulty
    image_url: Optional[str] = None


class Recipe(RecipeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class RecipeCreate(RecipeBase):
    pass #Class inherits from RecipeBase

class RecipeUpdate(SQLModel):  
    title: Optional[str] = None
    ingredients: Optional[List[str]] = None
    instructions_md: Optional[str] = None
    time_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    image_url: Optional[str] = None

