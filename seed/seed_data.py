import typer
from sqlmodel import Session
from app.database import engine, init_db
from app.models import Recipe, Difficulty

app = typer.Typer()


@app.command()
def fill():
    """Insert sample recipes into the database."""
    init_db()

    recipes = [
        Recipe(
            title="Spaghetti Meatball",
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
            image_url="http://localhost:8000/static/spagetti_meatballs.PNG"
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
            image_url="http://localhost:8000/static/chocolate_cake.PNG"
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
            image_url="http://localhost:8000/static/chocolatechip_cookies.JPG"
        ),

        Recipe(
            title="Hrira Soup",
            ingredients=[
                "1 chopped onion",
                "1 peeled and chopped tomato",
                "2 chopped celery stalks",
                "1 can chickpeas",
                "1 bunch fresh cilantro",
                "1 bunch fresh parsley",
                "1 cup green lentils",
                "2 tablespoons chicken soup powder",
                "1 teaspoon cumin",
                "1/2 teaspoon turmeric",
                "Salt and pepper, to taste",
                "1/4 cup flour",
                "Juice of 1 lemon",
                "1 cup noodles"
            ],
            instructions_md="""
### Cooking
1. In a large pot, sauté the onion and celery with a little canola oil.
2. Add the tomato, lentils, chickpeas, parsley, and cilantro, and cook briefly.
3. Add water until the pot is about 3/4 full, then add the spices.
4. Cook for about 1 hour.

### Thickening
1. In a small bowl, mix the flour with 1/2 cup cold water until smooth.
2. After one hour, slowly add the flour mixture to the soup while stirring constantly.

### Finish
- Add the noodles and the lemon juice.
- Serve hot 🔥
""",
            time_minutes=90,
            difficulty=Difficulty.easy,
            image_url="http://localhost:8000/static/hrira.PNG"
        ),

        Recipe(
            title="Cinnabons",
            ingredients=[
                "4 cups flour",
                "3/4 cup lukewarm water",
                "1/4 cup milk",
                "1 tablespoon dry yeast",
                "1/2 cup sugar",
                "2 eggs",
                "80 grams butter",
                "1 cup dark brown sugar (packed)",
                "1/2 cup light brown sugar",
                "3 level tablespoons cinnamon",
                "150 grams soft butter"
            ],
            instructions_md="""
### Dough
1. In a mixer bowl, combine the water, yeast, and sugar. Let sit for 10 minutes.
2. Add the milk, flour, eggs, and 80 grams of butter. Mix until smooth.
3. Let the dough rise for about 1 hour.

### Filling
- In a bowl, mix together the sugars and cinnamon.

### Shaping
1. Divide the dough into 2 parts.
2. Roll each part as thin as possible.
3. Spread with melted butter and sprinkle generously with the cinnamon mixture.
4. Fold the dough into a rectangle and roll slightly. Spread again with butter and cinnamon mixture.
5. Roll into a log.
6. Cut into cinnamon rolls about 7 cm wide.

### Baking
- Arrange the rolls in a baking pan.
- Bake at 170°C for about 30 minutes, or until golden brown.
""",
            time_minutes=120,
            difficulty=Difficulty.medium,
            image_url="http://localhost:8000/static/cinabom.JPG"
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
            image_url="http://localhost:8000/static/shnitzel.PNG"
        ),

        Recipe(
            title="Creamy Potatoes",
            ingredients=[
                "Boiled potatoes (cooked in water until tender)",
                "Crushed garlic",
                "1 package sliced button mushrooms",
                "50 g butter",
                "250 ml heavy cream (whipping cream)",
                "1 cup milk",
                "1/4 teaspoon nutmeg",
                "Salt and pepper, to taste",
                "100 g shredded yellow cheese"
            ],
            instructions_md="""
### Sauce
1. In a pot, sauté the butter, garlic, and mushrooms.
2. Add the cream, milk, and spices, and bring to a gentle boil.

### Assembly
1. Arrange the cooked potatoes in a baking dish.
2. Pour the cream mixture over the potatoes.

### Baking
1. Bake at 180°C for 30 minutes.
2. Sprinkle the shredded cheese on top and bake for another 30 minutes until golden.
""",
            time_minutes=60,
            difficulty=Difficulty.easy,
            image_url="http://localhost:8000/static/creamy_potatoes.PNG"
        ),

        Recipe(
            title="Jachnun",
            ingredients=[
                "1 kg flour",
                "1 packet baking powder",
                "1/4 cup sugar",
                "3 tablespoons date syrup (Silan)",
                "1 level teaspoon salt",
                "550 ml water",
                "200 g soft margarine",
                "2 cups canola oil"
            ],
            instructions_md="""
### Dough
1. In a mixer bowl, knead all the ingredients except the margarine and the oil for about 8 minutes.
2. The dough should be soft but not sticky. If needed, add a little more water.
3. Divide the dough into balls. Arrange them in a tray and pour 2 cups of oil over them. Let rest for 2 hours.

### Shaping
1. Roll each ball into a very thin, almost transparent sheet.
2. Spread margarine over the dough and roll it into a jachnun shape.
3. Arrange the prepared jachnun rolls in a jachnun pot.

### Baking
- Bake overnight at 100°C.
- Serve with crushed tomatoes.
""",
            time_minutes=5000,
            difficulty=Difficulty.hard,
            image_url="http://localhost:8000/static/jahnun.PNG"
        ),

        Recipe(
            title="Gyozas",
            ingredients=[
                "2 cups flour",
                "1/2 cup boiling water",
                "1 teaspoon salt",
                "Ground chicken thighs",
                "2 garlic cloves, crushed",
                "1 teaspoon grated ginger",
                "1 tablespoon sesame oil",
                "1 bunch green onions, chopped",
                "1/4 cup water",
                "Salt",
                "Pepper",
                "2 tablespoons oil (for frying)",
                "1/2 cup boiling water",
                "2 tablespoons soy sauce",
                "Crushed chili (to taste)",
                "1 teaspoon crushed garlic",
                "1 bunch green onions, chopped",
                "A little chopped cilantro",
                "1 teaspoon sesame oil",
                "3 tablespoons oil",
                "1/4 cup boiling water"
            ],
            instructions_md="""
### Dough
1. Mix flour with 1/2 cup boiling water and 1 teaspoon salt.
2. Let the dough rest for 30 minutes.
3. Meanwhile, prepare the filling.

### Filling
- Mix ground chicken thighs with crushed garlic, grated ginger, sesame oil, chopped green onions, 1/4 cup water, salt, and pepper.

### Shaping
1. Roll the dough and cut out circles.
2. Fill each circle with the filling and shape into gyozas.
3. Arrange the gyozas in a pan with a little oil.
4. Fry until the bottoms are browned, then add 1/2 cup boiling water and cover for 8 minutes.

### Dipping Sauce
- Mix soy sauce, crushed chili, crushed garlic, chopped green onions, chopped cilantro, sesame oil, 3 tablespoons oil, and 1/4 cup boiling water.
""",
            time_minutes=120,
            difficulty=Difficulty.hard,
            image_url="http://localhost:8000/static/giyozas.PNG"
        ),

        Recipe(
            title="Buns",
            ingredients=[
                "1 kg flour",
                "2 tablespoons dry yeast",
                "1/2 cup white sugar",
                "1/4 cup olive oil",
                "1 tablespoon salt",
                "500 ml cold water",
                "Sesame seeds"
            ],
            instructions_md="""
### Dough
1. In a mixer bowl, combine all the ingredients except the flour and the oil.
2. Knead for 8 minutes, then add the salt and the oil and continue kneading until smooth.
3. Let the dough rise for about 1 hour.

### Shaping
1. After rising, divide the dough into portions weighing 120 grams each.
2. Shape each portion into a bun.
3. Dip each bun first in a bowl of water and then in a bowl of sesame seeds.
4. Let the buns rise for another 30 minutes.

### Baking
- Bake in a preheated oven at **180°C** for about **40 minutes**.
""",
            time_minutes=120,
            difficulty=Difficulty.medium,
            image_url="http://localhost:8000/static/buns.PNG"
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
### Filling
1. Mix rice, grated tomato, onion, crushed garlic, parsley, **half the lemon juice**, salt, and pepper.

### Assembly
1. Slice a tomato and layer at the bottom of a pot with oil.
2. Stuff grape leaves with rice mixture and arrange neatly.

### Cooking Liquid
1. Mix olive oil, remaining lemon juice, silan, sliced garlic, salt, pepper, and **3 cups boiling water**.
2. Pour over grape leaves.

### Cooking
- Cook on low heat until rice is fully tender 🍃
""",
            time_minutes=60,
            difficulty=Difficulty.hard,
            image_url="http://localhost:8000/static/Yaprach.PNG"
        ),
    ]

    with Session(engine) as session:
        session.add_all(recipes)
        session.commit()


if __name__ == "__main__":
    app()