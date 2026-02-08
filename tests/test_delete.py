def test_delete_recipe(client, admin_headers):
    """Admin can delete an existing recipe"""

    new_recipe = {
        "title": "ToDelete",
        "ingredients": ["X", "Y"],
        "instructions_md": "## Instructions\nSomething",
        "time_minutes": 5,
        "difficulty": "Easy",
        "image_url": "https://example.com/test-delete.jpg",
    }

    create_response = client.post("/recipes", json=new_recipe, headers=admin_headers)
    assert create_response.status_code == 201
    recipe_id = create_response.json()["id"]

    delete_response = client.delete(f"/recipes/{recipe_id}", headers=admin_headers)
    assert delete_response.status_code == 200
    assert delete_response.json().get("message") == "Recipe deleted"


def test_delete_recipe_not_found(client, admin_headers):
    """Admin deleting a non-existing recipe → 404"""
    response = client.delete("/recipes/999999", headers=admin_headers)
    assert response.status_code == 404