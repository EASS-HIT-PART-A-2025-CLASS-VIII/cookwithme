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
            title="Meatball Pasta",
            ingredients=[
                "Cooked pasta",
                "1 can tomato paste",
                "4 cloves garlic",
                "1 tbsp chicken soup powder",
                "1 tbsp sugar",
                "500g ground meat",
                "1 grated onion",
                "1 tsp sweet paprika",
                "Salt and pepper",
            ],
            instructions_md="""
## Meatball Pasta

### Sauce
1. Heat oil in a large pot.
2. Fry **3 cloves of garlic** until fragrant.
3. Add tomato paste, sugar, chicken soup powder, salt, and pepper.
4. Add water halfway up the pot and bring to a boil.

### Meatballs
1. Mix ground meat, grated onion, garlic, paprika, salt, and pepper.
2. Shape into balls and gently add to the sauce.

### Finish
- Cook until meatballs are fully done.
- Mix with cooked pasta and serve hot 🍝
""",
            time_minutes=35,
            difficulty=Difficulty.medium,
            image_url="https://example.com/vodka.jpg"
        ),

        Recipe(
            title="Chocolate Cake",
            ingredients=[
                "4 eggs",
                "3/4 cup sugar",
                "3/4 cup canola oil",
                "1 cup flour",
                "1 baking powder",
                "1 cup chocolate drink powder",
                "1 whipping cream",
                "1 dark chocolate bar"
            ],
            instructions_md="""
## Chocolate Cake

### Cake Batter
1. Whisk eggs and sugar until light.
2. Add oil and mix gently.
3. Add flour, baking powder, chocolate powder, and **half of the whipping cream**.
4. Mix until smooth.

### Baking
- Bake in a preheated oven at **170–180°C** for **35 minutes**.

### Chocolate Topping
1. Melt dark chocolate with **½ cup whipping cream**.
2. Mix until smooth and glossy.
3. Pour over the baked cake 💝
""",
            time_minutes=45,
            difficulty=Difficulty.easy,
            image_url="https://example.com/pizza.jpg"
        ),

        Recipe(
            title="Chocolate Chip Cookies",
            ingredients=[
                "1 cup dark brown sugar",
                "1 cup white sugar",
                "200g soft butter",
                "2 eggs",
                "1 tsp vanilla extract",
                "2½ cups flour",
                "1 tsp baking powder",
                "2 cups chocolate chips"
            ],
            instructions_md="""
## Chocolate Chip Cookies

1. Cream butter with both sugars until smooth.
2. Add vanilla extract and eggs, mix well.
3. Add flour and baking powder and mix gently.
4. Fold in chocolate chips.

### Baking
- Bake at **170°C** for **9 minutes**.
- Cookies will soften as they cool 🍪
""",
            time_minutes=25,
            difficulty=Difficulty.easy,
            image_url="https://example.com/falafel.jpg"
        ),

        Recipe(
            title="Schnitzel",
            ingredients=[
                "500g chicken breast fillets",
                "1 tbsp mustard",
                "1 tbsp mayonnaise",
                "2 eggs",
                "1 tbsp sriracha",
                "Breadcrumbs",
                "Sesame seeds",
                "½ bottle canola oil",
                "Salt and pepper"
            ],
            instructions_md="""
## Chicken Schnitzel

### Marinade
1. Mix mustard, mayonnaise, eggs, sriracha, salt, and pepper.
2. Coat chicken fillets evenly.

### Coating
- Mix breadcrumbs with sesame seeds.
- Dip each fillet into the breadcrumb mixture.

### Frying
- Deep-fry in hot oil until **golden and fully cooked**.
""",
            time_minutes=30,
            difficulty=Difficulty.medium,
            image_url="https://example.com/salad.jpg"
        ),

        Recipe(
            title="Stuffed Grape Leaves (Yaprach)",
            ingredients=[
                "Fresh grape leaves (softened)",
                "2 cups round rice",
                "1 grated tomato",
                "1 grated onion",
                "3 crushed garlic cloves",
                "½ bunch chopped green onions",
                "½ bunch chopped parsley",
                "Juice of 2 lemons",
                "2 tbsp silan (date syrup)",
                "3 sliced garlic cloves",
                "½ cup olive oil",
                "Salt and pepper"
            ],
            instructions_md="""
## Stuffed Grape Leaves (Yaprach)

### Filling
1. Mix rice, grated tomato, onion, crushed garlic, parsley,
   **half the lemon juice**, salt, and pepper.

### Assembly
1. Slice a tomato and layer at the bottom of a pot with oil.
2. Stuff grape leaves with rice mixture and arrange neatly.

### Cooking Liquid
1. Mix olive oil, remaining lemon juice, silan,
   sliced garlic, salt, pepper, and **3 cups boiling water**.
2. Pour over grape leaves.

### Cooking
- Cook on low heat until rice is fully tender 🍃
""",
            time_minutes=60,
            difficulty=Difficulty.hard,
            image_url="https://example.com/shakshuka.jpg"
        ),
    ]

    with Session(engine) as session:
        session.add_all(recipes)
        session.commit()

    typer.echo("✅ 5 recipes inserted successfully")


if __name__ == "__main__":
    app()