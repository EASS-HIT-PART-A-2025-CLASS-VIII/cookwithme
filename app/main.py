from fastapi import FastAPI, HTTPException
from app.database import init_db
from app.models import Recipe, RecipeCreate, RecipeUpdate
from app.crud import (
    create_recipe,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe,
    delete_recipe,
)
from fastapi import Body

app = FastAPI(
    title="CookWithMe API",
    description="A clean and tested Recipe Management API built with FastAPI + SQLModel",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/recipes", response_model=Recipe, status_code=201)
def create_recipe_endpoint(recipe: RecipeCreate):
    return create_recipe(recipe)

@app.get("/recipes", response_model=list[Recipe])
def read_all():
    return get_all_recipes()

@app.get("/recipes/{recipe_id}", response_model=Recipe)
def read_one(recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe_endpoint(
    recipe_id: int,
    data: RecipeUpdate = Body(...)
):
    updated = update_recipe(recipe_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated

@app.delete("/recipes/{recipe_id}")
def delete_recipe_endpoint(recipe_id: int):
    deleted = delete_recipe(recipe_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"message": "Recipe deleted"}