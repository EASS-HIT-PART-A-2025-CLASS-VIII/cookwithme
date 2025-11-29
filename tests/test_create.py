def test_create_recipe(client):
    """Test for creating new recipe"""
    new_recipe = {
        "title": "Pizza",
        "ingredients": "Cheese, Dough",
        "instructions": "Bake in oven",
        "time_minutes": 20,
        "difficulty": "Medium",
        "image_url": "https://example.com/pizza.jpg"
    }

    response = client.post("/recipes", json=new_recipe)
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Pizza"
    assert data["difficulty"] == "Medium"
    assert data["image_url"] == "https://example.com/pizza.jpg"


def test_create_multiple_recipes(client):
    """Test creating multiple recipes"""
    recipes = [
        {
            "title": "Soup",
            "ingredients": "Water, Vegetables",
            "instructions": "Boil it well",
            "time_minutes": 15,
            "difficulty": "Easy",
            "image_url": "https://example.com/soup.jpg"
        },
        {
            "title": "Cake",
            "ingredients": "Flour, Sugar",
            "instructions": "Mix and bake",
            "time_minutes": 40,
            "difficulty": "Hard",
            "image_url": "https://example.com/cake.jpg"
        }
    ]

    ids = []

    for r in recipes:
        res = client.post("/recipes", json=r)
        assert res.status_code == 201
        ids.append(res.json()["id"])

    assert len(ids) == 2
