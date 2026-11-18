"""Settings, the top 10 table and the progress record for parents, saved as JSON.

Files live in the per-user data folder so they survive updates and the game
works from a read-only install. A damaged file is set aside, not fatal.
"""
import json
import os
import sys
import tempfile
import time

from . import WEB

ATTEMPTS_KEPT = 1000
TOP_N = 10
DIFFICULTIES = ("easy", "medium", "hard")


def data_dir():
    override = os.environ.get("BITFUSE_DATA")
    if override:
        path = override
    elif sys.platform == "win32":
        path = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "BitFuse")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        path = os.path.join(base, "bitfuse")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        path = os.path.join(tempfile.gettempdir(), "bitfuse")
        os.makedirs(path, exist_ok=True)
    return path


# In a web browser files vanish when the page closes, so saves go to the browser's localStorage.
def _web_storage():
    import platform  # pygbag's bridge to the page
    return platform.window.localStorage


def _load(name, default):
    if WEB:
        try:
            raw = _web_storage().getItem(f"bitfuse/{name}")
            data = json.loads(raw) if raw else default
            return data if isinstance(data, type(default)) else default
        except Exception:  # noqa: BLE001
            return default
    path = os.path.join(data_dir(), name)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, type(default)):
            return data
        raise ValueError("unexpected structure")
    except FileNotFoundError:
        return default
    except (OSError, ValueError):
        try:
            os.replace(path, path + ".corrupt")
        except OSError:
            pass
        return default


def _save(name, data):
    if WEB:
        try:
            _web_storage().setItem(f"bitfuse/{name}", json.dumps(data, ensure_ascii=False))
        except Exception as error:  # noqa: BLE001
            print(f"Could not save {name}: {error}", file=sys.stderr)
        return
    path = os.path.join(data_dir(), name)
    temp = path + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=1, ensure_ascii=False)
        os.replace(temp, path)
    except OSError as error:
        print(f"Could not save {name}: {error}", file=sys.stderr)


DEFAULT_SETTINGS = {"bgm": True, "sfx": True, "language": "en", "difficulty": "easy",
                    "fullscreen": False, "last_name": ""}


def load_settings():
    data = dict(DEFAULT_SETTINGS)
    data.update(_load("settings.json", {}))
    if data["difficulty"] not in DIFFICULTIES:
        data["difficulty"] = "easy"
    if data["language"] not in ("en", "ja"):
        data["language"] = "en"
    return data


def save_settings(settings):
    _save("settings.json", settings)


def load_scores():
    scores = [s for s in _load("scores.json", []) if isinstance(s, dict) and "score" in s]
    return sorted(scores, key=lambda s: -s["score"])[:TOP_N]


def qualifies(score):
    if score <= 0:
        return False
    scores = load_scores()
    return len(scores) < TOP_N or score > scores[-1]["score"]


def add_score(name, score, level, difficulty):
    scores = load_scores()
    entry = {"name": (name.strip() or "PLAYER")[:12], "score": int(score), "level": int(level),
             "difficulty": difficulty, "date": time.strftime("%Y-%m-%d"), "id": time.time()}
    scores.append(entry)
    scores = sorted(scores, key=lambda s: -s["score"])[:TOP_N]
    _save("scores.json", scores)
    return scores.index(entry) if entry in scores else -1


def load_progress():
    data = _load("progress.json", {})
    data.setdefault("games", 0)
    data.setdefault("attempts", [])
    best = data.setdefault("best_level", {})
    for d in DIFFICULTIES:
        best.setdefault(d, 0)
    return data


def record_game_start():
    data = load_progress()
    data["games"] += 1
    _save("progress.json", data)


def record_attempt(level, difficulty, target, bits, result, seconds, wrong, score):
    """result: 'solved', 'timeout' or 'quit'"""
    data = load_progress()
    data["attempts"].append({
        "when": time.strftime("%Y-%m-%d %H:%M"), "level": int(level), "difficulty": difficulty,
        "target": int(target), "bits": int(bits), "result": result, "seconds": round(seconds, 1),
        "wrong": int(wrong), "score": int(score),
    })
    data["attempts"] = data["attempts"][-ATTEMPTS_KEPT:]
    if result == "solved":
        data["best_level"][difficulty] = max(data["best_level"].get(difficulty, 0), int(level))
    _save("progress.json", data)


def reset_progress():
    _save("progress.json", {"games": 0, "attempts": [], "best_level": {d: 0 for d in DIFFICULTIES}})
    _save("scores.json", [])
