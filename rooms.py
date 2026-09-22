import random
import string

import storage

ROOM_GAMES = ("race", "sprint")
ROOM_TTL = 60 * 60 * 3  # 3 hours - rooms are cheap, just don't let them live forever
STALE_AFTER = 20  # seconds - a player who hasn't polled in this long is dropped

RACE_TEXTS = [
    "The lecturer says the wifi is fine right before the whole hall loses connection during the online quiz.",
    "Four hours before the deadline the group chat finally agrees on who is doing the slides.",
    "The library is silent except for one laptop fan trying to take off like a jet engine.",
    "Nobody read chapter three but everyone nods when the professor asks if it made sense.",
    "The printer works perfectly all semester then jams the exact moment the assignment is due.",
    "Somewhere on campus a first year is still looking for a lecture hall that does not exist.",
    "The exam is closed book except for the one formula everyone forgot to memorize.",
    "Coffee number three kicks in right as the code finally compiles without a single error.",
]

SPRINT_WORDS = (
    "the be to of and a in that have it for not on with he as you do at this but his by "
    "from they we say her she or an will my one all would there their what so up out if "
    "about who get which go me when make can like time no just him know take people into "
    "year your good some could them see other than then now look only come its over think "
    "also back after use two how our work first well way even new want because any these "
    "give day most us love code data type test game fast key line word run file page site "
    "web app user list task build net tool log bit byte loop true false null var let class "
    "push pull merge ship deploy fix speed logic input output stack queue graph tree array "
    "table query index cloud batch patch flag mode event state route theme timer clock "
    "light quick sharp brave smart clean solid cool exam deadline lecture campus library "
    "semester project wifi laptop coffee professor assignment groupchat quiz hostel gpa"
).split()


def _code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


def _key(game, code):
    return f"room:{game}:{code}"


def _player_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def _prune(room):
    """Drop players who've gone silent so a stale tab doesn't clutter the room."""
    t = storage.now()
    room["players"] = {
        pid: p for pid, p in room["players"].items()
        if t - p.get("last_seen", 0) < STALE_AFTER or p.get("done")
    }
    return room


def create(game, name):
    if game not in ROOM_GAMES:
        return None
    code = _code()
    pid = _player_id()
    t = storage.now()
    room = {
        "game": game,
        "code": code,
        "created": t,
        "started_at": None,
        "text": random.choice(RACE_TEXTS) if game == "race" else None,
        "words": random.sample(SPRINT_WORDS, 120) if game == "sprint" else None,
        "players": {
            pid: {"name": (name or "Player")[:20], "progress": 0, "wpm": 0,
                  "done": False, "joined": t, "last_seen": t}
        },
    }
    storage.set(_key(game, code), room, ROOM_TTL)
    return {"code": code, "player_id": pid, "room": room}


def join(game, code, name):
    room = storage.get(_key(game, code))
    if not room:
        return None, "room not found"
    if room["started_at"]:
        return None, "race already started"
    if len(room["players"]) >= 8:
        return None, "room is full"
    pid = _player_id()
    t = storage.now()
    room["players"][pid] = {"name": (name or "Player")[:20], "progress": 0, "wpm": 0,
                             "done": False, "joined": t, "last_seen": t}
    storage.set(_key(game, code), room, ROOM_TTL)
    return {"player_id": pid, "room": room}, None


def start(game, code):
    room = storage.get(_key(game, code))
    if not room:
        return None, "room not found"
    if not room["started_at"]:
        room["started_at"] = storage.now() + 3  # 3s synced countdown for everyone
        storage.set(_key(game, code), room, ROOM_TTL)
    return room, None


def update(game, code, pid, progress=None, wpm=None, done=None):
    room = storage.get(_key(game, code))
    if not room:
        return None, "room not found"
    p = room["players"].get(pid)
    if not p:
        return None, "not in this room"
    if progress is not None:
        p["progress"] = max(0, min(100, round(float(progress))))
    if wpm is not None:
        p["wpm"] = max(0, min(300, round(float(wpm))))
    if done is not None:
        p["done"] = bool(done)
    p["last_seen"] = storage.now()
    _prune(room)
    storage.set(_key(game, code), room, ROOM_TTL)
    return room, None


def get_room(game, code):
    room = storage.get(_key(game, code))
    if not room:
        return None
    _prune(room)
    return room
