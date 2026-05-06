"""Score routes."""

from flask import jsonify, request
from sqlalchemy import desc, select

from models import Game, Score
from validators import validate_score_payload


def register_score_routes(app):
    @app.post("/api/scores")
    def create_score():
        body = request.get_json(silent=True) or {}
        required = {"game_name", "player_name", "score", "level", "duration"}
        if not required.issubset(body.keys()):
            return jsonify({"success": False, "data": {}, "message": "Missing required fields"}), 400

        valid, message = validate_score_payload(body)
        if not valid:
            return jsonify({"success": False, "data": {}, "message": message}), 400

        player_name = str(body.get("player_name", "")).strip()
        if len(player_name) < 1 or len(player_name) > 100:
            return jsonify({"success": False, "data": {}, "message": "Invalid player_name"}), 400

        session_local = app.config["SessionLocal"]
        with session_local() as db:
            game = db.execute(select(Game).where(Game.name == body["game_name"])).scalar_one_or_none()
            if not game:
                return jsonify({"success": False, "data": {}, "message": "Game not found"}), 404

            score_obj = Score(
                game_name=body["game_name"],
                player_name=player_name,
                score=body["score"],
                level=body.get("level"),
                duration_seconds=body["duration"],
            )
            db.add(score_obj)
            db.commit()
            db.refresh(score_obj)
            # JSON uses `duration` to match POST /api/scores body (clients can resubmit payloads).
            return jsonify(
                {
                    "success": True,
                    "data": {
                        "id": score_obj.id,
                        "game_name": score_obj.game_name,
                        "player_name": score_obj.player_name,
                        "score": score_obj.score,
                        "level": score_obj.level,
                        "duration": score_obj.duration_seconds,
                        "timestamp": score_obj.timestamp.isoformat(),
                    },
                    "message": "Score saved",
                }
            )

    @app.get("/api/scores/<string:game_name>")
    def list_scores(game_name: str):
        session_local = app.config["SessionLocal"]
        with session_local() as db:
            game = db.execute(select(Game).where(Game.name == game_name)).scalar_one_or_none()
            if not game:
                return jsonify({"success": False, "data": {}, "message": "Game not found"}), 404

            rows = (
                db.execute(select(Score).where(Score.game_name == game_name).order_by(desc(Score.timestamp)))
                .scalars()
                .all()
            )
            data = [
                {
                    "id": item.id,
                    "game_name": item.game_name,
                    "player_name": item.player_name,
                    "score": item.score,
                    "level": item.level,
                    "duration": item.duration_seconds,
                    "timestamp": item.timestamp.isoformat(),
                }
                for item in rows
            ]
            return jsonify({"success": True, "data": data, "message": "Scores fetched"})

    @app.get("/api/scores/<string:game_name>/top10")
    def top_10_scores(game_name: str):
        session_local = app.config["SessionLocal"]
        with session_local() as db:
            game = db.execute(select(Game).where(Game.name == game_name)).scalar_one_or_none()
            if not game:
                return jsonify({"success": False, "data": {}, "message": "Game not found"}), 404

            rows = (
                db.execute(
                    select(Score)
                    .where(Score.game_name == game_name)
                    .order_by(desc(Score.score), Score.duration_seconds.asc(), Score.timestamp.asc())
                    .limit(10)
                )
                .scalars()
                .all()
            )
            data = [
                {
                    "id": item.id,
                    "player_name": item.player_name,
                    "score": item.score,
                    "level": item.level,
                    "duration": item.duration_seconds,
                    "timestamp": item.timestamp.isoformat(),
                }
                for item in rows
            ]
            return jsonify({"success": True, "data": data, "message": "Top 10 fetched"})
