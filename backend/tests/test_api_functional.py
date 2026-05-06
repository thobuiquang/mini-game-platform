"""Functional API tests (HTTP, headers, response shape)."""


def test_list_games_200(client) -> None:
    assert client.get("/api/v1/games").status_code == 200


def test_get_game_404(client) -> None:
    assert client.get("/api/v1/games/99999").status_code == 404


def test_search_short_query_400(client) -> None:
    assert client.get("/api/v1/games/search?q=a").status_code == 400
    assert client.get("/api/v1/games/search?q=%20%20").status_code == 400


def test_response_content_type(client) -> None:
    response = client.get("/api/v1/games")
    assert "application/json" in response.headers["content-type"]


def test_response_cors_headers(client) -> None:
    response = client.get("/api/v1/games", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in response.headers


def test_cors_wildcard_does_not_send_allow_credentials_true(client) -> None:
    """Wildcard origin + credentials=true is invalid per CORS; default * uses credentials=false."""
    response = client.get("/api/v1/games", headers={"Origin": "http://localhost:3000"})
    assert response.headers.get("access-control-allow-credentials", "").lower() != "true"


def test_response_has_required_fields(client) -> None:
    payload = client.get("/api/v1/games").json()
    assert {"success", "data", "pagination"}.issubset(payload.keys())


def test_error_response_format(client) -> None:
    payload = client.get("/api/v1/games/9999").json()
    assert payload["success"] is False
    assert "error" in payload


def test_health_endpoint_versioned(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body


def test_health_root_no_prefix(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body
