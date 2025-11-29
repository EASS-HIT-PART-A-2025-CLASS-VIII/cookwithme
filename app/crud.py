from sqlmodel import Session, select
from .models import Recipe, RecipeCreate, RecipeUpdate
from .database import engine


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

        # Convert only provided fields (exclude_unset=True)
        update_data = data.model_dump(exclude_unset=True)

        # Update recipe fields
        for key, value in update_data.items():
            setattr(recipe, key, value)

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