"""Automatic self-test: visits every screen and plays real levels to the fireworks.

Used by the build scripts to prove a packaged game really starts and plays:
    bitfuse --smoke-test result.txt
Set BITFUSE_SHOTS=<folder> to also save a screenshot of each screen.
"""
import os
import random
import sys
import tempfile
import traceback


def smoke_test(out_path=None):
    os.environ.setdefault("BITFUSE_DATA", tempfile.mkdtemp(prefix="bitfuse-smoke-"))
    shots = os.environ.get("BITFUSE_SHOTS")
    lines = []
    ok = True
    try:
        import pygame

        from . import levels, storage
        from .app import App
        from .scenes.credits import CreditsScene, LicenseScene
        from .scenes.game import GameScene
        from .scenes.intro import IntroScene
        from .scenes.parents import ParentGateScene, ParentsScene
        from .scenes.title import TitleScene

        app = App(windowed=True, smoke=True)
        count = {"n": 0}

        def frames(scene, n=20, name=None):
            for _ in range(n):
                pygame.event.pump()
                scene.update(1 / 60)
                scene.draw(app.canvas)
                app.present()
            if shots and name:
                os.makedirs(shots, exist_ok=True)
                count["n"] += 1
                pygame.image.save(app.canvas, os.path.join(shots, f"{count['n']:02d}_{name}.png"))

        # Every screen, in both languages
        for language in ("en", "ja"):
            app.set_language(language)
            for cls in (TitleScene, CreditsScene, LicenseScene, ParentGateScene, ParentsScene):
                scene = cls(app)
                app.switch(scene)
                frames(scene, 150 if cls is TitleScene else 10, f"{cls.__name__}_{language}")
            intro = IntroScene(app)
            app.switch(intro)
            for i in range(len(intro.entries)):
                intro._select(i)
                frames(intro, 200 if intro.entries[i][0] == "make" else 30,
                       f"intro_{intro.entries[i][0]}_{language}")
        lines.append("screens ok")
        app.set_language("en")

        # Play real levels on every difficulty, through the fuse and the fireworks
        solved = 0
        for diff in levels.DIFFICULTIES:
            game = GameScene(app, diff, seed=42)
            app.switch(game)
            for n in (1, 2, 3):
                frames(game, 4, f"game_{diff}_{n}_brief" if n == 1 else None)
                game.start_level()
                frames(game, 30, f"game_{diff}_{n}_play" if n == 1 else None)
                if n == 2:
                    # a wrong answer must fizzle and cost time
                    before = game.time_left
                    game.states = [1 - b for b in game.level.answer]
                    game.ignite()
                    for _ in range(600):
                        game.update(1 / 60)
                        if game.state == "play":
                            break
                    assert game.state == "play" and game.time_left < before - game.level.penalty + 1, "wrong accepted"
                game.states = list(game.level.answer)
                game.ignite()
                assert game.state == "burn" and game.correct, "right answer refused"
                for k in range(60 * 12):
                    pygame.event.pump()
                    game.update(1 / 60)
                    if k % 2 == 0:
                        game.draw(app.canvas)
                    if shots and n == 1 and k in (60, 200):
                        frames(game, 1, f"game_{diff}_burn_{k}")
                    if game.state == "show" and game.show_clock > 1.6 and n == 1 and diff == "easy":
                        frames(game, 1, f"game_{diff}_show")
                        break
                    if game.state == "brief":
                        break
                if game.state == "show":
                    game.after_show()
                assert game.state == "brief" and game.number == n + 1, f"{diff} level {n} did not advance"
                solved += 1
            # jump to big levels to see the biggest switch banks and shows
            for big in (50, 100):
                game.number = big
                game.new_level()
                game.start_level()
                frames(game, 20, f"game_{diff}_{big}")
                game.states = list(game.level.answer)
                game.ignite()
                for k in range(60 * 20):
                    game.update(1 / 60)
                    if k % 3 == 0:
                        game.draw(app.canvas)
                    if shots and game.state == "show" and abs(game.show_clock - 3.0) < 0.01:
                        frames(game, 1, f"game_{diff}_{big}_show")
                    if game.state in ("brief", "victory"):
                        break
                solved += 1
            assert game.state == "victory", f"{diff}: level 100 did not end in victory"
            game.name = "SMOKE"
            frames(game, 60, f"victory_{diff}")
            game.save_score()
            game.finish()
        lines.append(f"solved {solved} levels")

        # Time running out ends the game
        game = GameScene(app, "easy", seed=1)
        app.switch(game)
        game.start_level()
        game.time_left = 0.05
        frames(game, 5)
        assert game.state == "over", "time up did not end the game"
        frames(game, 5, "game_over")
        game.finish()

        # The generator must always give reachable numbers in the right range
        rng = random.Random(7)
        for _ in range(2000):
            diff = rng.choice(levels.DIFFICULTIES)
            lv = levels.generate(rng.randint(1, levels.LEVELS), diff, rng)
            assert 1 <= lv.target < (1 << lv.bits), "target out of range"
            assert levels.from_bits(lv.answer) == lv.target
        lines.append("generator ok")
        assert storage.load_scores(), "scores not saved"
        assert storage.load_progress()["attempts"], "progress not recorded"
        parents = ParentsScene(app)
        app.switch(parents)
        frames(parents, 5, "parents_filled")
        title = TitleScene(app)
        app.switch(title)
        frames(title, 5, "title_scores")
        app.audio.stop_loops()
        pygame.quit()
    except Exception:  # noqa: BLE001 - report every failure
        ok = False
        lines.append("FAILED\n" + traceback.format_exc())
    text = ("OK " if ok else "") + "; ".join(lines)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1
