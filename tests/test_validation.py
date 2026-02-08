import pytest


@pytest.fixture
def sample_recipe(client, admin_headers):
    """Create a sample recipe as admin (needed because create is admin-only)"""
    resp = client.post(
        "/recipes",
        json={
            "title": "Sample",
            "ingredients": ["Test Ingredient"],
            "instructions_md": "## Instructions\nCook well",
            "time_minutes": 10,
            "difficulty": "Easy",
            "image_url": "https://example.com/sample.jpg",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    return resp.json()


# ------------------------
# CREATE validation (admin-only endpoint)
# ------------------------

def test_create_recipe_invalid_title(client, admin_headers):
    """Too short title → 422"""
    resp = client.post(
        "/recipes",
        json={
            "title": "A",
            "ingredients": ["Sugar", "Milk"],
            "instructions_md": "## Instructions\nMix well",
            "time_minutes": 10,
            "difficulty": "Easy",
            "image_url": "https://example.com/img.jpg",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_create_recipe_negative_time(client, admin_headers):
    """Negative time → 422"""
    resp = client.post(
        "/recipes",
        json={
            "title": "Cake",
            "ingredients": ["Sugar"],
            "instructions_md": "## Instructions\nBake",
            "time_minutes": -5,
            "difficulty": "Hard",
            "image_url": "https://example.com/img.jpg",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_create_recipe_invalid_difficulty(client, admin_headers):
    """Invalid difficulty → 422"""
    resp = client.post(
        "/recipes",
        json={
            "title": "Pasta",
            "ingredients": ["Pasta", "Cheese"],
            "instructions_md": "## Instructions\nCook",
            "time_minutes": 15,
            "difficulty": "Impossible",
            "image_url": "https://example.com/img.jpg",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_create_recipe_missing_fields(client, admin_headers):
    """Missing required fields → 422"""
    resp = client.post("/recipes", json={"title": "Pasta"}, headers=admin_headers)
    assert resp.status_code == 422


def test_create_recipe_missing_image_url(client, admin_headers):
    """Image URL missing → 422"""
    resp = client.post(
        "/recipes",
        json={
            "title": "NoImage",
            "ingredients": ["A", "B"],
            "instructions_md": "## Instructions\nMix",
            "time_minutes": 10,
            "difficulty": "Easy",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_create_recipe_short_image_url(client, admin_headers):
    """Image URL too short → 422"""
    resp = client.post(
        "/recipes",
        json={
            "title": "Test",
            "ingredients": ["A", "B"],
            "instructions_md": "## Instructions\nMix",
            "time_minutes": 10,
            "difficulty": "Easy",
            "image_url": "a",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


# ------------------------
# UPDATE validation (admin-only endpoint)
# ------------------------

def test_update_recipe_short_title(client, admin_headers, sample_recipe):
    rid = sample_recipe["id"]
    resp = client.put(f"/recipes/{rid}", json={"title": "A"}, headers=admin_headers)
    assert resp.status_code == 422


def test_update_recipe_negative_time(client, admin_headers, sample_recipe):
    rid = sample_recipe["id"]
    resp = client.put(f"/recipes/{rid}", json={"time_minutes": -1}, headers=admin_headers)
    assert resp.status_code == 422


def test_update_recipe_invalid_difficulty(client, admin_headers, sample_recipe):
    rid = sample_recipe["id"]
    resp = client.put(f"/recipes/{rid}", json={"difficulty": "Impossible"}, headers=admin_headers)
    assert resp.status_code == 422


def test_update_recipe_invalid_image_url(client, admin_headers, sample_recipe):
    rid = sample_recipe["id"]
    resp = client.put(f"/recipes/{rid}", json={"image_url": "a"}, headers=admin_headers)
    assert resp.status_code == 422