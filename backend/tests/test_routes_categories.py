"""Integration tests for categories API."""


def test_get_categories_success(client) -> None:
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_category_has_game_count(client) -> None:
    response = client.get("/api/v1/categories")
    assert all("game_count" in category for category in response.json()["data"])
