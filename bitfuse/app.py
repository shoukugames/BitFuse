"""Window, main loop and screen switching.

The game draws onto a fixed 1280 x 720 canvas which is scaled to fit the
window, so it looks the same at any window size or in full screen (F11).
"""
import os
import random
import sys
import traceback

import pygame

from . import WEB, __version__, art, i18n, storage
from .audio import Audio
from .fireworks import Fireworks, prewarm
from .paths import asset

W, H = 1280, 720


class Scene:
    music = "title"

    def __init__(self, app):
        self.app = app

    def enter(self):
        pass

    def leave(self):
        pass

    def handle(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class Backdrop:
    """The night sky behind every menu, with an occasional quiet firework."""

    def __init__(self, app):
        self.app = app
        self.sky = None
        self.fx = None
        self.next = 1.5
        self.quiet = False

    def draw(self, surface, t, fireworks=True):
        if self.sky is None:
            self.sky = art.Sky((W, H))
            prewarm()
            self.fx = Fireworks((W, H), sound=self._sound)
        self.sky.draw(surface, t)
        if fireworks:
            self.next -= 1 / 60
            if self.next <= 0:
                self.next = random.uniform(2.2, 4.5)
                self.fx.launch(random.uniform(120, W - 120), self.sky.ground, random.choice(
                    ["peony", "ring", "willow", "palm", "double", "crossette"]), random.uniform(0.7, 1.0))
            self.fx.update(1 / 60)
            self.fx.draw(surface, 205)

    def _sound(self, name, pan=0.0):
        # distant fireworks on the menus: soft, and no rocket noise
        if name.startswith("boom"):
            self.app.audio.play("boom", pan, 0.25)


class App:
    def __init__(self, windowed=False, smoke=None):
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.key.set_repeat(400, 40)
        self.settings = storage.load_settings()
        i18n.LANG["current"] = self.settings["language"]
        self.smoke = smoke
        pygame.display.set_caption(f"BitFuse v{__version__}")
        try:
            icon = pygame.image.load(asset("icon.png"))
            pygame.display.set_icon(icon)
        except (pygame.error, FileNotFoundError):
            pass
        self.fullscreen = self.settings.get("fullscreen", False) and not windowed and not smoke
        self._make_window()
        self.canvas = pygame.Surface((W, H)).convert()
        self.audio = Audio(self.settings)
        self.backdrop = Backdrop(self)
        self.time = 0.0
        self.scene = None
        self.running = True
        self.mouse = (0, 0)

    def _make_window(self):
        if WEB:  # the page scales the canvas to fit the browser window
            self.window = pygame.display.set_mode((W, H))
        elif self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            info = pygame.display.Info()
            w, h = W, H
            if info.current_w and info.current_w < W + 40:
                scale = (info.current_w - 60) / W
                w, h = int(W * scale), int(H * scale)
            self.window = pygame.display.set_mode((w, h), pygame.RESIZABLE)

    def save(self):
        storage.save_settings(self.settings)

    def switch(self, scene):
        if self.scene:
            self.scene.leave()
        self.scene = scene
        self.audio.stop_loops()
        self.audio.music(scene.music)
        scene.enter()

    def set_language(self, code):
        self.settings["language"] = code
        i18n.LANG["current"] = code
        self.save()

    def _transform(self):
        ww, wh = self.window.get_size()
        scale = min(ww / W, wh / H)
        ox, oy = (ww - W * scale) / 2, (wh - H * scale) / 2
        return scale, ox, oy

    def to_canvas(self, pos):
        scale, ox, oy = self._transform()
        return (int((pos[0] - ox) / scale), int((pos[1] - oy) / scale))

    def present(self):
        if WEB and self.window.get_size() != (W, H):
            # pygbag can resize the page canvas after the game opened it; ask for the real size again
            self.window = pygame.display.set_mode((W, H))
        scale, ox, oy = self._transform()
        if abs(scale - 1) < 0.001 and ox == 0 and oy == 0:
            self.window.blit(self.canvas, (0, 0))
        else:
            self.window.fill((0, 0, 0))
            size = (int(W * scale), int(H * scale))
            self.window.blit(pygame.transform.smoothscale(self.canvas, size), (int(ox), int(oy)))
        pygame.display.flip()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.settings["fullscreen"] = self.fullscreen
        self.save()
        self._make_window()

    def frame(self, clock):
        dt = min(clock.tick(60) / 1000.0, 0.05)
        self.time += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = WEB  # in a browser there is nothing to quit to
                continue
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_F11 or
                                                 (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)) \
                    and not WEB:
                self.toggle_fullscreen()
                continue
            if hasattr(event, "pos") and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                                                       pygame.MOUSEMOTION):
                data = dict(event.dict)
                data["pos"] = self.to_canvas(event.pos)
                event = pygame.event.Event(event.type, data)
            self.scene.handle(event)
        self.mouse = self.to_canvas(pygame.mouse.get_pos())
        self.scene.update(dt)
        self.scene.draw(self.canvas)
        self.present()

    def run(self):
        from .scenes.title import TitleScene
        self.switch(TitleScene(self))
        clock = pygame.time.Clock()
        while self.running:
            self.frame(clock)
        self.audio.stop_loops()
        pygame.quit()

    async def run_web(self):
        """Browser main loop: hands control back to the page after every frame."""
        import asyncio
        from .scenes.title import TitleScene
        self.switch(TitleScene(self))
        clock = pygame.time.Clock()
        while True:  # a web page has no "quit"; closing the tab ends the game
            self.running = True
            self.frame(clock)
            await asyncio.sleep(0)


def _crash_log(error_text):
    try:
        path = os.path.join(storage.data_dir(), "crash.log")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(f"BitFuse v{__version__}\n{error_text}")
        return path
    except OSError:
        return None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--version" in argv:
        print(f"BitFuse v{__version__}")
        return 0
    if "--smoke-test" in argv:
        from .smoke import smoke_test
        i = argv.index("--smoke-test")
        out = argv[i + 1] if i + 1 < len(argv) else None
        return smoke_test(out)
    try:
        App(windowed="--windowed" in argv).run()
    except Exception:  # noqa: BLE001 - last-chance crash report
        text = traceback.format_exc()
        print(text, file=sys.stderr)
        _crash_log(text)
        return 1
    return 0
