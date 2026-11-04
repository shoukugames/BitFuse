import importlib

import pytest


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setenv("BITFUSE_DATA", str(tmp_path))
    from bitfuse import storage as module
    return importlib.reload(module)


def test_defaults(storage):
    s = storage.load_settings()
    assert s["bgm"] and s["language"] == "en" and s["difficulty"] == "easy"


def test_settings_round_trip(storage):
    s = storage.load_settings()
    s.update(bgm=False, language="ja", difficulty="hard")
    storage.save_settings(s)
    again = storage.load_settings()
    assert again["bgm"] is False and again["language"] == "ja" and again["difficulty"] == "hard"


def test_top_ten(storage):
    for i in range(15):
        storage.add_score(f"P{i}", i * 100 + 100, 3, "easy")
    scores = storage.load_scores()
    assert len(scores) == 10
    assert scores[0]["score"] == 1500
    assert not storage.qualifies(100)
    assert storage.qualifies(99999)


def test_progress(storage):
    storage.record_game_start()
    storage.record_attempt(4, "medium", 13, 4, "solved", 12.34, 1, 8600)
    storage.record_attempt(5, "medium", 21, 5, "timeout", 99, 2, 0)
    p = storage.load_progress()
    assert p["games"] == 1
    assert p["best_level"]["medium"] == 4
    assert p["attempts"][0]["seconds"] == 12.3
    storage.reset_progress()
    assert storage.load_progress()["attempts"] == []


def test_corrupt_file_is_set_aside(storage, tmp_path):
    (tmp_path / "scores.json").write_text("{not json")
    assert storage.load_scores() == []
    assert (tmp_path / "scores.json.corrupt").exists()
