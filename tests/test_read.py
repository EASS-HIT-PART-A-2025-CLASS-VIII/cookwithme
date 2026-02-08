def test_get_all_recipes_empty(client, user_headers):
    """Empty list test (requires login)"""
    response = client.get("/recipes", headers=user_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_recipes_after_creation(client, admin_headers, user_headers):
    """After admin creates a recipe, a logged-in user can see it in GET /recipes"""
    new_recipe = {
        "title": "Pasta",
        "ingredients": ["Pasta", "Cheese"],
        "instructions_md": "## Instructions\nBoil and mix",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/pasta.jpg",
    }

    create_response = client.post("/recipes", json=new_recipe, headers=admin_headers)
    assert create_response.status_code == 201

    list_response = client.get("/recipes", headers=user_headers)
    assert list_response.status_code == 200

    data = list_response.json()
    assert len(data) >= 1
    assert any(r["title"] == "Pasta" for r in data)


def test_get_recipe_by_id(client, admin_headers):
    """Recipe can be retrieved by ID"""
    new_recipe = {
        "title": "Salad",
        "ingredients": ["Lettuce", "Tomato"],
        "instructions_md": "## Instructions\nMix together",
        "time_minutes": 5,
        "difficulty": "Easy",
        "image_url": "https://example.com/salad.jpg",
    }

    create_response = client.post("/recipes", json=new_recipe, headers=admin_headers)
    assert create_response.status_code == 201

    recipe_id = create_response.json()["id"]

    get_response = client.get(f"/recipes/{recipe_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Salad"


def test_get_recipe_not_found(client):
    """Non-existing ID"""
    response = client.get("/recipes/999999")
    assert response.status_code == 404


def test_get_highlights(client):
    """Public highlights list"""
    res = client.get("/highlights")
    assert res.status_code == 200
    assert isinstance(res.json(), list)