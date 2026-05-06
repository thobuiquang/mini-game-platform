"""Boundary and edge-case API tests."""

from app.models.category import Category
from app.models.game import Game
from app.models.stats import GameStats


def test_empty_database(client, db_session) -> None:
    db_session.query(GameStats).delete()
    db_session.query(Game).delete()
    db_session.commit()
    payload = client.get("/api/v1/games").json()
    assert payload["data"] == []


def test_search_empty_results(client) -> None:
    payload = client.get("/api/v1/games/search?q=zzz").json()
    assert payload["data"] == []


def test_empty_category(client, db_session) -> None:
    db_session.add(Category(name="empty"))
    db_session.commit()
    payload = client.get("/api/v1/categories").json()["data"]
    target = [item for item in payload if item["name"] == "empty"][0]
    assert target["game_count"] == 0


def test_invalid_game_id_format(client) -> None:
    response = client.get("/api/v1/games/abc")
    assert response.status_code == 422


def test_invalid_pagination_params(client) -> None:
    response = client.get("/api/v1/games?page=abc&per_page=xyz")
    assert response.status_code == 422


def test_oversized_pagination(client) -> None:
    response = client.get("/api/v1/games?per_page=999")
    assert response.status_code == 422


def test_get_nonexistent_game(client) -> None:
    response = client.get("/api/v1/games/99999")
    assert response.status_code == 404


def test_update_nonexistent_game(client) -> None:
    response = client.post("/api/v1/games/99999/play", json={"session_time": 10})
    assert response.status_code == 404


def test_very_long_search_query(client) -> None:
    response = client.get(f"/api/v1/games/search?q={'a' * 1000}")
    assert response.status_code == 422


def test_unicode_search_query(client) -> None:
    response = client.get("/api/v1/games/search?q=Tiếng Việt")
    assert response.status_code == 200


def test_special_chars_search(client) -> None:
    response = client.get("/api/v1/games/search?q=game@#$%")
    assert response.status_code == 200


def test_duplicate_game_title(db_session) -> None:
    duplicate = Game(title="Game 1", game_path="dup")
    db_session.add(duplicate)
    try:
        db_session.commit()
    except Exception:
        assert True
    else:
        assert False


def test_null_required_fields(client) -> None:
    response = client.post("/api/v1/games/1/play", json={"session_time": -1})
    assert response.status_code == 422
