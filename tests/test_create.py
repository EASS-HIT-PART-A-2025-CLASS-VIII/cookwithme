def test_create_recipe(client, admin_headers):
    """Admin can create new recipe (EX3 security baseline)"""
    new_recipe = {
        "title": "Pizza",
        "ingredients": ["Cheese", "Dough"],
        "instructions_md": "## Instructions\nBake in oven",
        "time_minutes": 20,
        "difficulty": "Medium",
        "image_url": "https://example.com/pizza.jpg",
    }

    response = client.post("/recipes", json=new_recipe, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Pizza"
    assert data["difficulty"] == "Medium"
    assert data["image_url"] == "https://example.com/pizza.jpg"


def test_create_multiple_recipes(client, admin_headers):
    """Admin can create multiple recipes (EX3 security baseline)"""
    recipes = [
        {
            "title": "Soup",
            "ingredients": ["Water", "Vegetables"],
            "instructions_md": "## Instructions\nBoil it well",
            "time_minutes": 15,
            "difficulty": "Easy",
            "image_url": "https://example.com/soup.jpg",
        },
        {
            "title": "Cake",
            "ingredients": ["Flour", "Sugar"],
            "instructions_md": "## Instructions\nMix and bake",
            "time_minutes": 40,
            "difficulty": "Hard",
            "image_url": "https://example.com/cake.jpg",
        },
    ]

    ids = []
    for r in recipes:
        res = client.post("/recipes", json=r, headers=admin_headers)
        assert res.status_code == 201
        ids.append(res.json()["id"])

    assert len(ids) == 2