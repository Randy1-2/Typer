# Deploying to Vercel

## 1. Push this folder to a GitHub repo, then import it in Vercel.
Vercel will detect `vercel.json` and build it as a Python (Flask) project automatically.

## 2. Important: link a KV store before you rely on multiplayer or leaderboards
Vercel's filesystem is read-only in production and each request can land on a
different instance, so the old approach (writing to a local `scores.json`
file) does **not** persist there. This project already handles that for you
(`storage.py`) — it just needs somewhere to write to:

1. In your Vercel project → **Storage** tab → **Create Database** → **KV**
   (Upstash-powered, free tier is enough for this).
2. Connect it to the project. Vercel injects `KV_REST_API_URL` and
   `KV_REST_API_TOKEN` automatically — no code changes needed.
3. Redeploy.

**Without a linked KV store:** the site still works, but scores and
multiplayer rooms are only stored in `/tmp` on the current serverless
instance, so a friend joining your race from a different instance/region
may not see your room. Locally (`python app.py`), everything works out of
the box using plain JSON files in `static/json/` — no setup needed for
development or testing multiplayer with two browser tabs on your machine.

## 3. Local dev
```
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000, then open a second tab to test a multiplayer
room against yourself.

## What's multiplayer right now
- **Race** and **60s Sprint** support live rooms: create a room, share the
  5-character code, everyone races/types the same passage or word list at
  the same synced start time, with live progress bars for each player.
- Word Rain, Sudden Death and Unscramble are solo for now (they got new
  campus-themed word pools, streak call-outs, and a speed ramp instead) —
  say the word if you'd like rooms/leaderboards added to those too.
