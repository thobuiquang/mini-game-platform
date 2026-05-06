"""API endpoint tests."""


def test_get_games(client):
    response = client.get("/api/games")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 5


def test_get_game_detail_ok(client):
    response = client.get("/api/games/flappy")
    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["name"] == "flappy"


def test_get_game_detail_not_found(client):
    response = client.get("/api/games/unknown")
    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_post_score_ok(client):
    response = client.post(
        "/api/scores",
        json={"game_name": "flappy", "player_name": "Tester", "score": 5, "level": 1, "duration": 10},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["game_name"] == "flappy"
    assert body["data"]["duration"] == 10
    assert "duration_seconds" not in body["data"]


def test_score_response_can_be_resubmitted_as_post_body(client):
    """GET/POST score JSON uses `duration` like POST input so clients can round-trip."""
    first = client.post(
        "/api/scores",
        json={
            "game_name": "brick_breaker",
            "player_name": "Roundtrip",
            "score": 100,
            "level": 2,
            "duration": 42,
        },
    )
    assert first.status_code == 200
    payload = first.get_json()["data"]
    resubmit = {
        "game_name": payload["game_name"],
        "player_name": payload["player_name"],
        "score": payload["score"],
        "level": payload["level"],
        "duration": payload["duration"],
    }
    second = client.post("/api/scores", json=resubmit)
    assert second.status_code == 200


def test_post_score_invalid_payload(client):
    response = client.post(
        "/api/scores",
        json={"game_name": "snake", "player_name": "Tester", "score": 30, "level": 1, "duration": 10},
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_get_scores_by_game(client):
    response = client.get("/api/scores/tetris")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_top10_scores(client):
    response = client.get("/api/scores/brick_breaker/top10")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) <= 10
