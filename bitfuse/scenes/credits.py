"""Credits and the full GPL 3.0 licence text."""
import os

import pygame

from .. import RELEASE_DATE, __version__, art, i18n
from ..app import Scene
from ..paths import root
from ..ui import Button, ButtonGroup


def _back(app):
    from .title import TitleScene
    app.switch(TitleScene(app))


class CreditsScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.buttons = ButtonGroup([
            Button((20, 20, 150, 50), lambda: i18n.t("back"), lambda: _back(app), color=(90, 100, 140), size=20),
            Button((640 - 130, 610, 260, 54), lambda: i18n.t("view_license"),
                   lambda: app.switch(LicenseScene(app)), color=(52, 96, 190), size=20),
        ])

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            _back(self.app)
            return
        self.buttons.handle(event, self.app.audio)

    def update(self, dt):
        self.t += dt
        self.buttons.update(self.app.mouse, dt)

    def draw(self, surface):
        self.app.backdrop.draw(surface, self.t)
        box = pygame.Rect(240, 40, 800, 640)
        art.panel(surface, box, radius=26, alpha=230)
        logo = art.gradient_text("BitFuse", 64, (255, 236, 150), (255, 120, 40), outline=(40, 14, 4))
        surface.blit(logo, logo.get_rect(midtop=(640, 58)))
        art.text(surface, i18n.t("credits_title"), (640, 146), 22, art.TEXT_DIM, anchor="midtop")
        rows = [
            (i18n.t("version"), f"v{__version__}"),
            (i18n.t("date"), RELEASE_DATE),
            (i18n.t("creator"), "Shawn Rapaz"),
            (i18n.t("built_with"), "Claude Code"),
            (i18n.t("website"), "https://shoukugames.org/"),
            (i18n.t("email"), "info@shoukugames.org"),
            (i18n.t("license"), "GNU GPL v3.0"),
        ]
        y = 196
        for label, value in rows:
            art.text(surface, label, (620, y), 20, art.TEXT_DIM, anchor="topright")
            art.text(surface, value, (650, y), 20, art.GOLD if label == i18n.t("creator") else art.TEXT)
            y += 38
        art.paragraph(surface, i18n.t("license_text"), (270, y + 8, 740, 60), 15, art.TEXT_DIM, align="center")
        art.text(surface, i18n.t("fonts_credit"), (640, y + 66), 14, art.TEXT_DIM, anchor="midtop")
        art.text(surface, i18n.t("audio_credit"), (640, y + 88), 14, art.TEXT_DIM, anchor="midtop")
        art.text(surface, i18n.t("ages"), (640, y + 116), 16, art.PINK, anchor="midtop")
        self.buttons.draw(surface)


class LicenseScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.scroll = 0.0
        try:
            with open(os.path.join(root(), "LICENSE"), encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            text = "GNU GENERAL PUBLIC LICENSE Version 3\nhttps://www.gnu.org/licenses/gpl-3.0.html"
        self.lines = []
        for para in text.split("\n"):
            self.lines.extend(art.wrap(para, 15, 1060, "regular") if para.strip() else [""])
        self.view = pygame.Rect(90, 96, 1100, 590)
        self.buttons = ButtonGroup([
            Button((20, 20, 150, 50), lambda: i18n.t("back"), lambda: app.switch(CreditsScene(app)),
                   color=(90, 100, 140), size=20)])

    def max_scroll(self):
        return max(0, len(self.lines) * 20 - self.view.h + 30)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.switch(CreditsScene(self.app))
                return
            step = {pygame.K_DOWN: 60, pygame.K_UP: -60, pygame.K_PAGEDOWN: 500, pygame.K_PAGEUP: -500,
                    pygame.K_HOME: -10 ** 9, pygame.K_END: 10 ** 9}.get(event.key, 0)
            self.scroll = max(0, min(self.max_scroll(), self.scroll + step))
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(self.max_scroll(), self.scroll - event.y * 60))
        self.buttons.handle(event, self.app.audio)

    def update(self, dt):
        self.t += dt
        self.buttons.update(self.app.mouse, dt)

    def draw(self, surface):
        self.app.backdrop.draw(surface, self.t, fireworks=False)
        art.text(surface, "GNU General Public License v3.0", (640, 30), 28, art.TEXT, anchor="midtop", shadow=True)
        art.panel(surface, self.view.inflate(20, 20), radius=16, alpha=240)
        clip = surface.get_clip()
        surface.set_clip(self.view)
        first = int(self.scroll // 20)
        for i in range(first, min(len(self.lines), first + self.view.h // 20 + 2)):
            art.text(surface, self.lines[i], (self.view.x + 10, self.view.y + 10 + i * 20 - self.scroll), 15,
                     art.TEXT, "regular")
        surface.set_clip(clip)
        total = self.max_scroll()
        if total:
            bar_h = max(40, self.view.h * self.view.h / (total + self.view.h))
            y = self.view.y + (self.view.h - bar_h) * self.scroll / total
            pygame.draw.rect(surface, (90, 110, 190), (self.view.right + 2, y, 6, bar_h), border_radius=3)
        self.buttons.draw(surface)
