"""Unit tests for game validators."""

from validators.game_validators import validate_score_payload


def test_brick_breaker_valid():
    ok, _ = validate_score_payload(
        {"game_name": "brick_breaker", "player_name": "A", "score": 10, "level": 1, "duration": 30}
    )
    assert ok is True


def test_brick_breaker_invalid_level():
    ok, _ = validate_score_payload(
        {"game_name": "brick_breaker", "player_name": "A", "score": 10, "level": 0, "duration": 30}
    )
    assert ok is False


def test_caro_valid():
    ok, _ = validate_score_payload(
        {
            "game_name": "caro",
            "player_name": "A",
            "score": 1,
            "level": 1,
            "duration": 30,
            "board_state": [["X", "O", ""], ["", "X", ""], ["O", "", ""]],
        }
    )
    assert ok is True


def test_caro_invalid_score():
    ok, _ = validate_score_payload(
        {"game_name": "caro", "player_name": "A", "score": 2, "level": 1, "duration": 20, "board_state": [["", "", ""], ["", "", ""], ["", "", ""]]}
    )
    assert ok is False


def test_flappy_invalid_speed():
    ok, _ = validate_score_payload(
        {"game_name": "flappy", "player_name": "A", "score": 20, "level": 1, "duration": 10}
    )
    assert ok is False


def test_snake_valid():
    ok, _ = validate_score_payload(
        {"game_name": "snake", "player_name": "A", "score": 5, "level": 1, "duration": 20}
    )
    assert ok is True


def test_tetris_invalid_lines_level_logic():
    ok, _ = validate_score_payload(
        {"game_name": "tetris", "player_name": "A", "score": 100, "level": 1, "duration": 50, "lines_cleared": 30}
    )
    assert ok is False
