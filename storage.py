"""
Tiny key/value storage layer.

Local dev: reads/writes JSON files under DATA_DIR (persists on disk).
Production on Vercel: the filesystem is read-only and every request can hit a
fresh instance, so plain JSON files won't hold state (leaderboards, and
especially multiplayer rooms, need to be shared across requests/players).
If Vercel KV (or any Upstash-compatible Redis) is linked to the project,
its env vars are picked up automatically and used instead - no code changes
needed. Without one, the app still runs but falls back to /tmp, which is
fine for local testing but NOT reliable for real multiplayer in production.
"""
import json
import os
import time

import requests

BASE = os.path.dirname(os.path.abspath(__file__))
IS_VERCEL = bool(os.environ.get("VERCEL"))
DATA_DIR = "/tmp/typer-data" if IS_VERCEL else os.path.join(BASE, "static", "json")
os.makedirs(DATA_DIR, exist_ok=True)

# Vercel KV env vars, or plain Upstash Redis REST env vars - either works.
KV_URL = os.environ.get("KV_REST_API_URL") or os.environ.get("UPSTASH_REDIS_REST_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN") or os.environ.get("UPSTASH_REDIS_REST_TOKEN")


def kv_configured():
    return bool(KV_URL and KV_TOKEN)


def _cmd(*args):
    r = requests.post(
        KV_URL,
        headers={"Authorization": f"Bearer {KV_TOKEN}"},
        json=list(args),
        timeout=5,
    )
    r.raise_for_status()
    return r.json().get("result")


def _safe_key(key):
    return "".join(c if c.isalnum() or c in "-_:." else "_" for c in key)


def _file_path(key):
    return os.path.join(DATA_DIR, _safe_key(key) + ".json")


def get(key, default=None):
    if kv_configured():
        try:
            raw = _cmd("GET", key)
            return json.loads(raw) if raw is not None else default
        except Exception:
            return default
    try:
        with open(_file_path(key), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def set(key, value, ttl_seconds=None):
    if kv_configured():
        try:
            raw = json.dumps(value)
            if ttl_seconds:
                _cmd("SET", key, raw, "EX", str(ttl_seconds))
            else:
                _cmd("SET", key, raw)
        except Exception:
            pass
        return
    path = _file_path(key)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def now():
    return time.time()
