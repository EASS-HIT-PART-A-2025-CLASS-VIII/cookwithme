import typer
from sqlmodel import Session
from app.database import engine, init_db
from app.models import Recipe, Difficulty

app = typer.Typer()

@app.command()
def fill():
    """Insert 5 sample recipes into the database."""
    init_db()

    recipes = [
        Recipe(
            title="Pasta alla Vodka",
            ingredients=[
                "Pasta",
                "Tomato paste",
                "Vodka",
                "Cream",
                "Garlic",
                "Onion"
            ],
            instructions="Cook pasta. Prepare sauce. Mix together.",
            time_minutes=25,
            difficulty=Difficulty.easy,
            image_url="https://example.com/vodka.jpg"
        ),
        Recipe(
            title="Margherita Pizza",
            ingredients=[
                "Dough",
                "Tomato sauce",
                "Mozzarella",
                "Basil"
            ],
            instructions="Bake pizza and add basil.",
            time_minutes=30,
            difficulty=Difficulty.medium,
            image_url="https://example.com/pizza.jpg"
        ),
        Recipe(
            title="Falafel",
            ingredients=[
                "Chickpeas",
                "Onion",
                "Garlic",
                "Parsley"
            ],
            instructions="Blend, shape balls, and fry.",
            time_minutes=30,
            difficulty=Difficulty.medium,
            image_url="https://example.com/falafel.jpg"
        ),
        Recipe(
            title="Greek Salad",
            ingredients=[
                "Tomatoes",
                "Cucumber",
                "Feta",
                "Olives"
            ],
            instructions="Chop and mix ingredients.",
            time_minutes=10,
            difficulty=Difficulty.easy,
            image_url="https://example.com/salad.jpg"
        ),
        Recipe(
            title="Shakshuka",
            ingredients=[
                "Eggs",
                "Tomatoes",
                "Onion",
                "Spices"
            ],
            instructions="Simmer sauce and cook eggs.",
            time_minutes=25,
            difficulty=Difficulty.medium,
            image_url="https://example.com/shakshuka.jpg"
        ),
    ]

    with Session(engine) as session:
        session.add_all(recipes)
        session.commit()

    typer.echo("✅ 5 recipes inserted successfully")


if __name__ == "__main__":
    app()