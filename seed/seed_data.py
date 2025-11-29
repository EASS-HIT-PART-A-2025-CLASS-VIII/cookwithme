import typer
from sqlmodel import Session
from app.database import engine, init_db
from app.models import Recipe

app = typer.Typer()

@app.command()
def fill():
    """Insert 5 sample recipes into the database."""
    init_db()

    recipes = [
        Recipe(
            title="Pasta alla Vodka",
            ingredients="Pasta, tomato paste, vodka, cream, garlic, onion",
            instructions="Cook pasta. Prepare sauce. Mix together.",
            time_minutes=25,
            difficulty="Easy",
            image_url="https://example.com/vodka.jpg"
        ),
        Recipe(
            title="Margherita Pizza",
            ingredients="Dough, tomato sauce, mozzarella, basil",
            instructions="Bake pizza and add basil.",
            time_minutes=30,
            difficulty="Medium",
            image_url="https://example.com/pizza.jpg"
        ),
        Recipe(
            title="Falafel",
            ingredients="Chickpeas, onion, garlic, parsley",
            instructions="Blend, shape balls, and fry.",
            time_minutes=30,
            difficulty="Medium",
            image_url="https://example.com/falafel.jpg"
        ),
        Recipe(
            title="Greek Salad",
            ingredients="Tomatoes, cucumber, feta, olives",
            instructions="Chop and mix ingredients.",
            time_minutes=10,
            difficulty="Easy",
            image_url="https://example.com/salad.jpg"
        ),
        Recipe(
            title="Shakshuka",
            ingredients="Eggs, tomatoes, onion, spices",
            instructions="Simmer sauce and cook eggs.",
            time_minutes=25,
            difficulty="Medium",
            image_url="https://example.com/shakshuka.jpg"
        ),
    ]

    with Session(engine) as session:
        session.add_all(recipes)
        session.commit()

    typer.echo("✅ 5 recipes inserted successfully")

if __name__ == "__main__":
    app()