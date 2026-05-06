"""Small helpers used across routes."""


def game_play_url(game_path: str) -> str:
    """Return URL path to a game's index.html under static mount."""
    return f"/static/games/{game_path}/index.html"
