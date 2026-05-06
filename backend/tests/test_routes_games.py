"""Integration tests for games API."""

from app.models.category import Category
from app.models.game import Game


def test_get_games_success(client) -> None:
    response = client.get("/api/v1/games")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_get_games_pagination(client) -> None:
    response = client.get("/api/v1/games?page=2&per_page=10")
    payload = response.json()
    assert payload["pagination"]["page"] == 2
    assert len(payload["data"]) == 5


def test_get_games_filter_category(client) -> None:
    response = client.get("/api/v1/games?category=action")
    assert response.status_code == 200
    assert all(item["category"] == "action" for item in response.json()["data"])


def test_get_games_sort_by_rating(client) -> None:
    response = client.get("/api/v1/games?sort_by=rating")
    data = response.json()["data"]
    assert data[0]["rating"] >= data[-1]["rating"]


def test_get_games_invalid_page(client) -> None:
    response = client.get("/api/v1/games?page=-1")
    assert response.status_code == 422


def test_get_game_by_id_success(client) -> None:
    response = client.get("/api/v1/games/1")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == 1


def test_get_game_invalid_id(client) -> None:
    response = client.get("/api/v1/games/9999")
    assert response.status_code == 404


def test_play_count_increments_via_post(client) -> None:
    first = client.get("/api/v1/games/1").json()["data"]["play_count"]
    client.post("/api/v1/games/1/play", json={"session_time": 0})
    second = client.get("/api/v1/games/1").json()["data"]["play_count"]
    assert second == first + 1


def test_search_game_by_name(client) -> None:
    response = client.get("/api/v1/games/search?q=Game 1")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0


def test_search_game_invalid_query(client) -> None:
    response = client.get("/api/v1/games/search?q=a")
    assert response.status_code == 400


def test_search_no_results(client) -> None:
    response = client.get("/api/v1/games/search?q=zzzzzz")
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_search_literal_underscore_not_wildcard(client, db_session) -> None:
    category = db_session.query(Category).filter_by(name="puzzle").first()
    assert category is not None
    db_session.add_all(
        [
            Game(title="puzzle_1", game_path="puzzle-underscore", version="1.0.0", category_id=category.id),
            Game(title="puzzleA1", game_path="puzzle-a1", version="1.0.0", category_id=category.id),
        ]
    )
    db_session.commit()

    response = client.get("/api/v1/games/search?q=puzzle_1")
    assert response.status_code == 200
    titles = {item["title"] for item in response.json()["data"]}
    assert "puzzle_1" in titles
    assert "puzzleA1" not in titles
