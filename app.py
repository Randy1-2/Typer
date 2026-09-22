import time
from flask import Flask, jsonify, request, abort, render_template

import storage
import rooms

BASE_GAMES = ("typing-test", "race", "rain", "sprint", "survival", "scramble")

app = Flask(__name__, static_folder="static", template_folder="templates", static_url_path="/static")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/poems")
def poems():
    return jsonify(storage.get("poems", {}))


@app.get("/api/scores/<game>")
def get_scores(game):
    if game not in BASE_GAMES:
        abort(404)
    scores = storage.get("scores", {}).get(game, [])
    scores.sort(key=lambda s: (-s["wpm"], -s["accuracy"]))
    return jsonify(scores[:10])


@app.post("/api/scores/<game>")
def add_score(game):
    if game not in BASE_GAMES:
        abort(404)
    d = request.get_json(silent=True) or {}
    try:
        entry = {
            "name": (str(d.get("name", "")).strip() or "anonymous")[:20],
            "wpm": max(0, min(300, round(float(d["wpm"])))),
            "accuracy": max(0, min(100, round(float(d.get("accuracy", 100))))),
            "text": str(d.get("text", ""))[:60],
            "time": int(time.time()),
        }
    except (KeyError, ValueError, TypeError):
        return jsonify(error="wpm must be a number"), 400
    db = storage.get("scores", {})
    db.setdefault(game, []).append(entry)
    storage.set("scores", db)
    return jsonify(entry), 201


# ---- multiplayer rooms (race + sprint) ----

@app.post("/api/rooms/<game>")
def create_room(game):
    d = request.get_json(silent=True) or {}
    result = rooms.create(game, d.get("name"))
    if not result:
        abort(404)
    return jsonify(result), 201


@app.post("/api/rooms/<game>/<code>/join")
def join_room(game, code):
    d = request.get_json(silent=True) or {}
    result, err = rooms.join(game, code.upper(), d.get("name"))
    if err:
        return jsonify(error=err), 400
    return jsonify(result)


@app.post("/api/rooms/<game>/<code>/start")
def start_room(game, code):
    room, err = rooms.start(game, code.upper())
    if err:
        return jsonify(error=err), 404
    return jsonify(room)


@app.post("/api/rooms/<game>/<code>/update")
def update_room(game, code):
    d = request.get_json(silent=True) or {}
    room, err = rooms.update(
        game, code.upper(), d.get("player_id"),
        progress=d.get("progress"), wpm=d.get("wpm"), done=d.get("done"),
    )
    if err:
        return jsonify(error=err), 404
    return jsonify(room)


@app.get("/api/rooms/<game>/<code>")
def get_room(game, code):
    room = rooms.get_room(game, code.upper())
    if not room:
        abort(404)
    return jsonify(room)


# ---- pages ----

@app.get("/typing-test")
def typing_test():
    return render_template("typing-test.html")


@app.get("/race")
def race():
    return render_template("race.html")


@app.get("/games")
def games():
    return render_template("games.html")


@app.get("/rain")
def rain():
    return render_template("rain.html")


@app.get("/sprint")
def sprint():
    return render_template("sprint.html")


@app.get("/scramble")
def scramble():
    return render_template("scramble.html")


@app.get("/survival")
def survival():
    return render_template("survival.html")


@app.get("/hack")
def hack():
    return render_template("hack.html")


@app.get("/memory")
def memory():
    return render_template("memory.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
