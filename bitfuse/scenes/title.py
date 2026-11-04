"""Title screen: menu, settings, top 10 and the animated logo."""
import math

import pygame

from .. import __version__, art, i18n, storage
from ..app import H, W, Scene
from ..levels import DIFFICULTIES
from ..ui import Button, ButtonGroup

DIFF_COLORS = {"easy": (40, 160, 90), "medium": (200, 140, 30), "hard": (200, 60, 70)}
OFF_COLOR = (54, 62, 100)


class TitleScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.scores = storage.load_scores()
        s = app.settings
        x, w = 64, 330
        self.buttons = ButtonGroup([
            Button((x, 236, w, 76), lambda: i18n.t("play"), self.play, color=(220, 110, 40), size=34),
            Button((x, 328, w, 58), lambda: i18n.t("intro"), self.intro, color=(52, 96, 190), size=24),
            Button((x, 400, w, 58), lambda: i18n.t("parents"), self.parents, color=(110, 70, 170), size=24),
            Button((x, 472, w, 58), lambda: i18n.t("credits"), self.credits, color=(40, 120, 150), size=24),
            Button((x, 544, w, 58), lambda: i18n.t("quit"), self.quit, color=(90, 96, 130), size=22),
        ])
        px = 440
        self.diff_buttons = {}
        for i, d in enumerate(DIFFICULTIES):
            b = Button((px + 20 + i * 128, 292, 120, 46), (lambda d=d: i18n.t(d)), (lambda d=d: self.set_diff(d)),
                       size=18)
            self.diff_buttons[d] = b
            self.buttons.add(b)
        self.lang_buttons = {
            "en": Button((px + 20, 470, 186, 44), "English", lambda: self.set_lang("en"), size=18),
            "ja": Button((px + 214, 470, 186, 44), "日本語", lambda: self.set_lang("ja"), size=18),
        }
        for b in self.lang_buttons.values():
            self.buttons.add(b)
        self.bgm_button = self.buttons.add(Button((px + 20, 560, 186, 44), self._bgm_label, self.toggle_bgm, size=18))
        self.sfx_button = self.buttons.add(Button((px + 214, 560, 186, 44), self._sfx_label, self.toggle_sfx, size=18))
        self._colors()
        self.s = s

    # ------------------------------------------------------------ actions
    def _bgm_label(self):
        return f"{i18n.t('bgm')}: {i18n.t('on') if self.app.settings['bgm'] else i18n.t('off')}"

    def _sfx_label(self):
        return f"{i18n.t('sfx')}: {i18n.t('on') if self.app.settings['sfx'] else i18n.t('off')}"

    def _colors(self):
        s = self.app.settings
        for d, b in self.diff_buttons.items():
            b.color = DIFF_COLORS[d] if s["difficulty"] == d else OFF_COLOR
        for code, b in self.lang_buttons.items():
            b.color = (52, 96, 190) if s["language"] == code else OFF_COLOR
        self.bgm_button.color = (40, 150, 120) if s["bgm"] else OFF_COLOR
        self.sfx_button.color = (40, 150, 120) if s["sfx"] else OFF_COLOR

    def set_diff(self, d):
        self.app.settings["difficulty"] = d
        self.app.save()
        self._colors()

    def set_lang(self, code):
        self.app.set_language(code)
        self._colors()

    def toggle_bgm(self):
        self.app.settings["bgm"] = not self.app.settings["bgm"]
        self.app.save()
        self.app.audio.refresh_music(self.music)
        self._colors()

    def toggle_sfx(self):
        self.app.settings["sfx"] = not self.app.settings["sfx"]
        self.app.save()
        self._colors()

    def play(self):
        from .game import GameScene
        self.app.audio.play("start")
        self.app.switch(GameScene(self.app, self.app.settings["difficulty"]))

    def intro(self):
        from .intro import IntroScene
        self.app.switch(IntroScene(self.app))

    def parents(self):
        from .parents import ParentGateScene
        self.app.switch(ParentGateScene(self.app))

    def credits(self):
        from .credits import CreditsScene
        self.app.switch(CreditsScene(self.app))

    def quit(self):
        self.app.running = False

    # ------------------------------------------------------------ loop
    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.play()
                return
            if event.key == pygame.K_ESCAPE:
                self.quit()
                return
        self.buttons.handle(event, self.app.audio)

    def update(self, dt):
        self.t += dt
        self.buttons.update(self.app.mouse, dt)

    def draw_logo(self, surface):
        cx, y = W // 2, 30
        logo = art.gradient_text("BitFuse", 96, (255, 236, 150), (255, 120, 40), outline=(40, 14, 4))
        rect = logo.get_rect(midtop=(cx, y))
        pulse = 0.5 + 0.5 * math.sin(self.t * 1.6)
        art.blit_glow(surface, rect.center, 300, (120, 50, 10), 0.35 + 0.15 * pulse)
        surface.blit(logo, rect)
        # a fuse under the logo, burning from left to right over and over
        fy = rect.bottom + 6
        x1, x2 = rect.left + 10, rect.right - 10
        phase = (self.t * 0.35) % 1.3
        spark_x = x1 + (x2 - x1) * min(1.0, phase)
        art.aaline(surface, art.FUSE_DARK, (x1, fy), (x2, fy), 7)
        art.aaline(surface, art.FUSE, (x1, fy), (x2, fy), 4)
        for bx in range(int(x1), int(x2), 7):
            pygame.draw.aaline(surface, (205, 160, 100), (bx - 2, fy - 3), (bx + 2, fy + 3))
        if phase < 1.0:
            art.aaline(surface, (30, 26, 28), (x1, fy), (spark_x, fy), 6)
            art.blit_glow(surface, (spark_x, fy), 34, (255, 170, 60), 1.0)
            art.blit_glow(surface, (spark_x, fy), 10, (255, 255, 220), 1.0)
        # binary for "BIT" floating across
        bits = "01000010 01001001 01010100"
        for i, ch in enumerate(bits):
            k = 0.5 + 0.5 * math.sin(self.t * 2 + i * 0.5)
            art.text(surface, ch, (cx - 210 + i * 16.2, fy + 14), 15, art.mix((60, 70, 120), art.ACCENT, k),
                     "display", anchor="midtop")
        art.text(surface, i18n.t("title_sub"), (cx, fy + 40), 20, art.TEXT, anchor="midtop", shadow=True)

    def draw(self, surface):
        self.app.backdrop.draw(surface, self.t)
        self.draw_logo(surface)
        s = self.app.settings
        # settings panel
        px = 440
        art.panel(surface, (px, 236, 420, 386), radius=20, alpha=215)
        art.text(surface, i18n.t("difficulty"), (px + 20, 252), 20, art.GOLD)
        info = i18n.t(s["difficulty"] + "_info")
        art.paragraph(surface, info, (px + 22, 350, 380, 90), 15, art.TEXT_DIM, spacing=1.35)
        art.text(surface, i18n.t("language"), (px + 20, 438), 20, art.GOLD)
        art.text(surface, i18n.t("settings"), (px + 20, 528), 20, art.GOLD)
        # top 10
        tx = 890
        art.panel(surface, (tx, 236, 326, 386), radius=20, alpha=215)
        art.text(surface, i18n.t("top10"), (tx + 163, 250), 24, art.GOLD, anchor="midtop", shadow=True)
        if not self.scores:
            art.paragraph(surface, i18n.t("no_scores"), (tx + 20, 400, 286, 80), 18, art.TEXT_DIM, align="center")
        for i, entry in enumerate(self.scores):
            y = 292 + i * 32
            color = [art.GOLD, (220, 224, 240), (230, 160, 100)][i] if i < 3 else art.TEXT
            if i % 2 == 0:
                pygame.draw.rect(surface, (30, 38, 80), (tx + 10, y - 3, 306, 29), border_radius=6)
            art.text(surface, f"{i + 1}", (tx + 34, y), 18, color, "display", anchor="midtop")
            art.text(surface, entry["name"], (tx + 54, y), 17, color)
            diff = entry.get("difficulty", "easy")
            art.text(surface, i18n.t(diff)[:6], (tx + 196, y + 3), 12, DIFF_COLORS.get(diff, art.TEXT_DIM),
                     anchor="midtop")
            art.text(surface, f"{entry['score']:,}", (tx + 306, y), 17, color, anchor="topright")
        self.buttons.draw(surface)
        # footer
        badge = pygame.Rect(64, 640, 330, 40)
        pygame.draw.rect(surface, (180, 40, 60), badge, border_radius=20)
        pygame.draw.rect(surface, (255, 150, 160), badge, 2, border_radius=20)
        art.text(surface, i18n.t("ages"), badge.center, 18, art.TEXT, anchor="center")
        art.text(surface, f"v{__version__}  ·  shoukugames.org  ·  GPL-3.0", (W - 30, H - 52), 15, art.TEXT_DIM,
                 anchor="topright")
