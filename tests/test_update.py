def test_update_recipe(client):
    """Test updating an existing recipe"""

    # Create
    new_recipe = {
        "title": "Original",
        "ingredients": ["A", "B",],
        "instructions": "Do something",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/original.jpg"
    }

    create_response = client.post("/recipes", json=new_recipe)
    assert create_response.status_code == 201

    recipe = create_response.json()
    recipe_id = recipe["id"]

    # Update
    update_data = {
        "title": "Updated Title",
        "ingredients": ["New Ingredients",],
        "instructions": "New Instructions",
        "time_minutes": 20,
        "difficulty": "Medium",
        "image_url": "https://example.com/updated.jpg"
    }

    update_response = client.put(f"/recipes/{recipe_id}", json=update_data)
    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated["title"] == "Updated Title"
    assert updated["ingredients"] == ["New Ingredients",]
    assert updated["instructions"] == "New Instructions"
    assert updated["time_minutes"] == 20
    assert updated["difficulty"] == "Medium"
    assert updated["image_url"] == "https://example.com/updated.jpg"


def test_update_recipe_not_found(client):
    """Test updating a recipe that does not exist"""

    update_data = {
        "title": "Doesn't matter",
        "image_url": "https://example.com/test.jpg"
    }

    response = client.put("/recipes/999999", json=update_data)

    assert response.status_code == 404
