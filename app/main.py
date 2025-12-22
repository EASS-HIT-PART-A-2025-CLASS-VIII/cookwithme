from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from app.seed.seed_data import run_seed
from app.database import init_db, get_session
from app.models import Recipe, RecipeCreate, RecipeUpdate, Review, ReviewCreate
from app.crud import (
    create_recipe,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe,
    delete_recipe,
)

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --------------------------
# RECIPES CRUD
# --------------------------

@app.post("/recipes", response_model=Recipe, status_code=201)
def create_recipe_endpoint(recipe: RecipeCreate):
    return create_recipe(recipe)


@app.get("/recipes", response_model=list[Recipe])
def read_all():
    return get_all_recipes()


@app.get("/recipes/{recipe_id}", response_model=Recipe)
def read_one(recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")
    return recipe


@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe_endpoint(recipe_id: int, data: RecipeUpdate):
    updated = update_recipe(recipe_id, data)
    if not updated:
        raise HTTPException(404, "Recipe not found")
    return updated


@app.delete("/recipes/{recipe_id}")
def delete_recipe_endpoint(recipe_id: int):
    deleted = delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(404, "Recipe not found")
    return {"message": "Deleted"}


# --------------------------
# REVIEWS
# --------------------------

@app.post("/recipes/{recipe_id}/reviews", response_model=Review)
def add_review(
    recipe_id: int,
    review: ReviewCreate,
    session: Session = Depends(get_session)
):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    new_review = Review(
        recipe_id=recipe_id,
        rating=review.rating,
        comment=review.comment,
    )

    session.add(new_review)
    session.commit()
    session.refresh(new_review)
    return new_review


@app.get("/recipes/{recipe_id}/reviews", response_model=list[Review])
def get_reviews(recipe_id: int, session: Session = Depends(get_session)):
    statement = select(Review).where(Review.recipe_id == recipe_id)
    return session.exec(statement).all()