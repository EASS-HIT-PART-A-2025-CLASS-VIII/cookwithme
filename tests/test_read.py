def test_get_all_recipes_empty(client):
    """Empty list test"""
    response = client.get("/recipes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_recipes_after_creation(client):
    """Test that after creating a recipe, it appears in GET"""
    new_recipe = {
        "title": "Pasta",
        "ingredients": ["Pasta", "Cheese",],
        "instructions": "Boil and mix",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/pasta.jpg"
    }

    create_response = client.post("/recipes", json=new_recipe)
    assert create_response.status_code == 201

    list_response = client.get("/recipes")
    data = list_response.json()

    assert list_response.status_code == 200
    assert len(data) >= 1
    assert any(r["title"] == "Pasta" for r in data)


def test_get_recipe_by_id(client):
    """Test that a recipe can be retrieved by ID"""
    new_recipe = {
        "title": "Salad",
        "ingredients": ["Lettuce", "Tomato",],
        "instructions": "Mix together",
        "time_minutes": 5,
        "difficulty": "Easy",
        "image_url": "https://example.com/salad.jpg"
    }

    create_response = client.post("/recipes", json=new_recipe)
    assert create_response.status_code == 201

    recipe = create_response.json()
    recipe_id = recipe["id"]

    get_response = client.get(f"/recipes/{recipe_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Salad"


def test_get_recipe_not_found(client):
    """Test requesting a non-existing ID"""
    response = client.get("/recipes/999999")
    assert response.status_code == 404