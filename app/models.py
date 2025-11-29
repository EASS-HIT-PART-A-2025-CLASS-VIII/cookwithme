from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum


# Difficulty Enum
class Difficulty(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


# Base class shared by Create & DB model
class RecipeBase(SQLModel):
    title: str = Field(
        min_length=2,
        description="Short title of the recipe"
    )

    ingredients: str = Field(
        min_length=3,
        description="Comma-separated list of ingredients"
    )

    instructions: str = Field(
        min_length=5,
        description="Step-by-step instructions"
    )

    time_minutes: int = Field(
        gt=0,
        description="Preparation time in minutes"
    )

    difficulty: Difficulty = Field(
        description="Recipe difficulty level"
    )


    image_url: str = Field(
        min_length=5,
        max_length=500,
        description="Image URL of the recipe"
    )


# Database model
class Recipe(RecipeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Create model
class RecipeCreate(RecipeBase):
    pass


# Update model (all optional)
class RecipeUpdate(SQLModel):
    title: Optional[str] = Field(
        default=None,
        min_length=2,
        description="Short title of the recipe"
    )

    ingredients: Optional[str] = Field(
        default=None,
        min_length=3,
        description="Updated list of ingredients"
    )

    instructions: Optional[str] = Field(
        default=None,
        min_length=5,
        description="Updated instructions"
    )

    time_minutes: Optional[int] = Field(
        default=None,
        gt=0,
        description="Updated preparation time"
    )

    difficulty: Optional[Difficulty] = Field(
        default=None,
        description="Updated difficulty level"
    )


    image_url: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=500,
        description="Updated image URL"
    )