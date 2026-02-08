def test_recommendations_endpoint_works(client, user_headers):
    res = client.get("/recommendations?limit=3", headers=user_headers)
    assert res.status_code == 200

    body = res.json()
    assert "recommendations" in body
    assert isinstance(body["recommendations"], list)