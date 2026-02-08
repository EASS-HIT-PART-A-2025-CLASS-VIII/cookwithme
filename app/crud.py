from typing import Optional, List
from sqlmodel import Session, select

from .models import Recipe, RecipeCreate, RecipeUpdate, Highlight, User
from .security import hash_password, verify_password


# ------------------------
# Recipes
# ------------------------

def get_all_recipes(session: Session) -> List[Recipe]:
    return session.exec(select(Recipe)).all()


def get_recipe_by_id(session: Session, recipe_id: int) -> Optional[Recipe]:
    return session.get(Recipe, recipe_id)


def create_recipe(session: Session, data: RecipeCreate) -> Recipe:
    recipe = Recipe(**data.model_dump())
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


def update_recipe(session: Session, recipe_id: int, data: RecipeUpdate) -> Optional[Recipe]:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return None

    payload = data.model_dump(exclude_unset=True)
    for k, v in payload.items():
        setattr(recipe, k, v)

    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


def delete_recipe(session: Session, recipe_id: int) -> Optional[Recipe]:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return None

    session.delete(recipe)
    session.commit()
    return recipe


# ------------------------
# Highlights
# ------------------------

def create_highlight(session: Session, highlight: Highlight) -> Highlight:
    session.add(highlight)
    session.commit()
    session.refresh(highlight)
    return highlight


def get_all_highlights(session: Session) -> List[Highlight]:
    return session.exec(select(Highlight)).all()


# ------------------------
# Users / Auth
# ------------------------

def create_user(session: Session, email: str, password: str, name: str, role: str = "user") -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name.strip(),
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user