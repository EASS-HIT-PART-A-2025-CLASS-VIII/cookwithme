def test_delete_recipe(client):
    """Test deleting an existing recipe"""

    # Create recipe
    new_recipe = {
        "title": "ToDelete",
        "ingredients": "X, Y",
        "instructions": "Something",
        "time_minutes": 5,
        "difficulty": "Easy",
        "category": "Test",
        "image_url": "https://example.com/test-delete.jpg"
    }

    create_response = client.post("/recipes", json=new_recipe)
    assert create_response.status_code == 201

    recipe_id = create_response.json()["id"]

    # Delete
    delete_response = client.delete(f"/recipes/{recipe_id}")
    assert delete_response.status_code == 200

    data = delete_response.json()

    # Assert returned message only
    assert "message" in data
    assert data["message"] == "Recipe deleted"


def test_delete_recipe_not_found(client):
    """Test deleting a recipe that does not exist"""
    response = client.delete("/recipes/999999")
    assert response.status_code == 404