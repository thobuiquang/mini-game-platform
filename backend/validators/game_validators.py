"""Game-specific score validation."""

from typing import Any

VALID_GAMES = {"brick_breaker", "caro", "flappy", "snake", "tetris"}


def _validate_caro_board(board_state: Any) -> bool:
    if not isinstance(board_state, list) or len(board_state) != 3:
        return False
    x_count = 0
    o_count = 0
    for row in board_state:
        if not isinstance(row, list) or len(row) != 3:
            return False
        for cell in row:
            if cell not in {"X", "O", ""}:
                return False
            if cell == "X":
                x_count += 1
            elif cell == "O":
                o_count += 1
    return abs(x_count - o_count) <= 1


def validate_score_payload(payload: dict[str, Any]) -> tuple[bool, str]:
    game_name = payload.get("game_name")
    score = payload.get("score")
    level = payload.get("level")
    duration = payload.get("duration")

    if game_name not in VALID_GAMES:
        return False, "Invalid game_name"
    if not isinstance(score, int):
        return False, "score must be integer"
    if not isinstance(duration, int) or duration <= 0:
        return False, "duration must be > 0"

    if game_name == "brick_breaker":
        if score < 0:
            return False, "brick_breaker: score must be >= 0"
        if not isinstance(level, int) or level < 1:
            return False, "brick_breaker: level must be >= 1"
        return True, "Valid score"

    if game_name == "caro":
        if score not in {-1, 0, 1}:
            return False, "caro: score must be -1, 0, or 1"
        board_state = payload.get("board_state")
        if not _validate_caro_board(board_state):
            return False, "caro: invalid board_state"
        return True, "Valid score"

    if game_name == "flappy":
        if score < 0:
            return False, "flappy: score must be >= 0"
        if score > duration:
            return False, "flappy: score cannot exceed duration"
        return True, "Valid score"

    if game_name == "snake":
        if score < 0:
            return False, "snake: score must be >= 0"
        if score > (duration // 2):
            return False, "snake: score too high for duration"
        return True, "Valid score"

    if game_name == "tetris":
        lines_cleared = payload.get("lines_cleared")
        if score < 0:
            return False, "tetris: score must be >= 0"
        if not isinstance(level, int) or level < 1:
            return False, "tetris: level must be >= 1"
        if not isinstance(lines_cleared, int) or lines_cleared < 0:
            return False, "tetris: lines_cleared must be >= 0"
        expected_level = (lines_cleared // 10) + 1
        if level < expected_level:
            return False, "tetris: level inconsistent with lines_cleared"
        return True, "Valid score"

    return False, "Unsupported game"
