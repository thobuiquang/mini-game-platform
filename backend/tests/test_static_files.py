"""Static file serving tests."""


def test_serve_game_html(client) -> None:
    response = client.get("/static/games/game1/index.html")
    assert response.status_code == 200


def test_serve_game_assets(client) -> None:
    response = client.get("/static/games/game1/js/game.js")
    assert response.status_code == 200


def test_static_file_not_found(client) -> None:
    response = client.get("/static/games/nonexist.html")
    assert response.status_code == 404


def test_static_path_traversal_blocked(client) -> None:
    response = client.get("/static/games/../../etc/passwd")
    assert response.status_code == 404
