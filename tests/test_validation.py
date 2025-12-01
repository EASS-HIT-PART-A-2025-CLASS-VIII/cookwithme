import pytest


@pytest.fixture
def sample_recipe(client):
    """Create a sample recipe using the API"""
    resp = client.post("/recipes", json={
        "title": "Sample",
        "ingredients": ["Test Ingredient",],
        "instructions": "Cook well",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/sample.jpg"
    })
    assert resp.status_code == 201
    return resp.json()


def test_create_recipe_invalid_title(client):
    """Too short title → 422"""
    resp = client.post("/recipes", json={
        "title": "A",
        "ingredients": ["Sugar", "Milk",],
        "instructions": "Mix well",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/img.jpg"
    })
    assert resp.status_code == 422


def test_create_recipe_negative_time(client):
    """Negative time → 422"""
    resp = client.post("/recipes", json={
        "title": "Cake",
        "ingredients": ["Sugar",],
        "instructions": "Bake",
        "time_minutes": -5,
        "difficulty": "Hard",
        "image_url": "https://example.com/img.jpg"
    })
    assert resp.status_code == 422


def test_create_recipe_invalid_difficulty(client):
    """Invalid difficulty → 422"""
    resp = client.post("/recipes", json={
        "title": "Pasta",
        "ingredients": ["Pasta","Cheese",],
        "instructions": "Cook",
        "time_minutes": 15,
        "difficulty": "Impossible",
        "image_url": "https://example.com/img.jpg"
    })
    assert resp.status_code == 422


def test_create_recipe_missing_fields(client):
    """Missing required fields → 422"""
    resp = client.post("/recipes", json={
        "title": "Pasta"
    })
    assert resp.status_code == 422


def test_create_recipe_missing_image_url(client):
    """Image URL missing → 422"""
    resp = client.post("/recipes", json={
        "title": "NoImage",
        "ingredients": ["A", "B",],
        "instructions": "Mix",
        "time_minutes": 10,
        "difficulty": "Easy"
    })
    assert resp.status_code == 422


def test_create_recipe_short_image_url(client):
    """Image URL too short → 422"""
    resp = client.post("/recipes", json={
        "title": "Test",
        "ingredients": ["A", "B",],
        "instructions": "Mix",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "a"
    })
    assert resp.status_code == 422


def test_update_recipe_short_title(client, sample_recipe):
    """Updating title too short → 422"""
    recipe_id = sample_recipe["id"]

    resp = client.put(f"/recipes/{recipe_id}", json={
        "title": "X"
    })
    assert resp.status_code == 422


def test_update_recipe_negative_time(client, sample_recipe):
    """Negative time on update → 422"""
    recipe_id = sample_recipe["id"]

    resp = client.put(f"/recipes/{recipe_id}", json={
        "time_minutes": -1
    })
    assert resp.status_code == 422


def test_update_recipe_invalid_difficulty(client, sample_recipe):
    """Invalid difficulty on update → 422"""
    recipe_id = sample_recipe["id"]

    resp = client.put(f"/recipes/{recipe_id}", json={
        "difficulty": "Nightmare"
    })
    assert resp.status_code == 422


def test_update_recipe_invalid_image_url(client, sample_recipe):
    """Image_url too short on update → 422"""
    recipe_id = sample_recipe["id"]

    resp = client.put(f"/recipes/{recipe_id}", json={
        "image_url": "x"
    })
    assert resp.status_code == 422