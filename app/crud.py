from sqlmodel import Session, select
from .models import Recipe, RecipeCreate, RecipeUpdate
from .database import engine
from fastapi import HTTPException


def get_all_recipes():
    with Session(engine) as session:
        return session.exec(select(Recipe)).all()


def get_recipe_by_id(recipe_id: int):
    with Session(engine) as session:
        return session.get(Recipe, recipe_id)


def create_recipe(data: RecipeCreate):
    with Session(engine) as session:
        # Convert RecipeCreate → Recipe model, includes category + image_url
        recipe = Recipe(**data.model_dump())
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
        return recipe


def update_recipe(recipe_id: int, data: RecipeUpdate):
    with Session(engine) as session:
        recipe = session.get(Recipe, recipe_id)
        if not recipe:
            return None

        if data.title is not None:
            if len(data.title) < 2:
                raise HTTPException(status_code=422, detail="Title too short")
            recipe.title = data.title

        if data.ingredients is not None:
            recipe.ingredients = data.ingredients

        if data.instructions is not None:
            recipe.instructions = data.instructions

        if data.time_minutes is not None:
            if data.time_minutes <= 0:
                raise HTTPException(status_code=422)
            recipe.time_minutes = data.time_minutes

        if data.difficulty is not None:
            recipe.difficulty = data.difficulty

        if data.image_url is not None:
            if len(data.image_url) < 5:
                raise HTTPException(status_code=422)
            recipe.image_url = data.image_url

        session.commit()
        session.refresh(recipe)
        return recipe


def delete_recipe(recipe_id: int):
    with Session(engine) as session:
        recipe = session.get(Recipe, recipe_id)
        if not recipe:
            return None

        session.delete(recipe)
        session.commit()
        return recipe