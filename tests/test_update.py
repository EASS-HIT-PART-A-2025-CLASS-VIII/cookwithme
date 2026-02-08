def test_update_recipe(client, admin_headers):
    """Admin can update an existing recipe"""

    create_response = client.post(
        "/recipes",
        json={
            "title": "Original",
            "ingredients": ["A", "B"],
            "instructions_md": "## Instructions\nDo something",
            "time_minutes": 10,
            "difficulty": "Easy",
            "image_url": "https://example.com/original.jpg",
        },
        headers=admin_headers,
    )
    assert create_response.status_code == 201
    recipe_id = create_response.json()["id"]

    update_response = client.put(
        f"/recipes/{recipe_id}",
        json={
            "title": "Updated Title",
            "ingredients": ["New Ingredients"],
            "instructions_md": "## Instructions\nNew Instructions",
            "time_minutes": 20,
            "difficulty": "Medium",
            "image_url": "https://example.com/updated.jpg",
        },
        headers=admin_headers,
    )
    assert update_response.status_code == 200


def test_update_recipe_not_found(client, admin_headers):
    """Admin updating non-existing recipe -> 404"""
    response = client.put(
        "/recipes/999999",
        json={"title": "Doesn't matter", "image_url": "https://example.com/test.jpg"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_update_recipe_user_forbidden(client, admin_headers, user_headers):
    """Normal user cannot update recipes -> 403"""

    create_response = client.post(
        "/recipes",
        json={
            "title": "Protected",
            "ingredients": ["X"],
            "instructions_md": "## Instructions\nDo",
            "time_minutes": 5,
            "difficulty": "Easy",
            "image_url": "https://example.com/x.jpg",
        },
        headers=admin_headers,
    )
    assert create_response.status_code == 201
    recipe_id = create_response.json()["id"]

    response = client.put(
        f"/recipes/{recipe_id}",
        json={"title": "Hack"},
        headers=user_headers,
    )
    assert response.status_code == 403