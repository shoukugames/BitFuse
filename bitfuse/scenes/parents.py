"""Parents Only: a simple grown-up check, then the progress record."""
import random

import pygame

from .. import art, i18n, storage
from ..app import Scene
from ..levels import DIFFICULTIES
from ..ui import Button, ButtonGroup

DIFF_COLORS = {"easy": (40, 160, 90), "medium": (200, 140, 30), "hard": (200, 60, 70)}


def _back(app):
    from .title import TitleScene
    app.switch(TitleScene(app))


class ParentGateScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.a, self.b = random.randint(6, 9), random.randint(6, 9)
        self.entry = ""
        self.wrong = 0.0
        self.buttons = ButtonGroup([Button((20, 22, 150, 50), lambda: i18n.t("back"), lambda: _back(app),
                                           color=(90, 100, 140), size=20)])
        for i, label in enumerate(["7", "8", "9", "4", "5", "6", "1", "2", "3", "←", "0", "OK"]):
            col, row = i % 3, i // 3
            rect = (520 + col * 84, 330 + row * 72, 76, 62)
            color = (30, 160, 90) if label == "OK" else (60, 80, 130)
            self.buttons.add(Button(rect, label, (lambda k=label: self.key(k)), color=color, size=26, kind="display"))

    def key(self, k):
        if k == "←":
            self.entry = self.entry[:-1]
        elif k == "OK":
            self.check()
        elif len(self.entry) < 3:
            self.entry += k

    def check(self):
        if self.entry == str(self.a * self.b):
            self.app.switch(ParentsScene(self.app))
        else:
            self.wrong = 2.0
            self.entry = ""
            self.app.audio.play("error")
            self.a, self.b = random.randint(6, 9), random.randint(6, 9)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                _back(self.app)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.check()
            elif event.key == pygame.K_BACKSPACE:
                self.entry = self.entry[:-1]
            elif event.unicode and event.unicode.isdigit() and len(self.entry) < 3:
                self.entry += event.unicode
        self.buttons.handle(event, self.app.audio)

    def update(self, dt):
        self.t += dt
        self.wrong = max(0.0, self.wrong - dt)
        self.buttons.update(self.app.mouse, dt)

    def draw(self, surface):
        self.app.backdrop.draw(surface, self.t)
        art.panel(surface, (400, 90, 480, 600), radius=24)
        en, ja = i18n.both("parent_gate")
        art.text(surface, i18n.t("parents"), (640, 110), 34, art.TEXT, anchor="midtop")
        art.text(surface, en, (640, 160), 16, art.TEXT_DIM, anchor="midtop")
        art.text(surface, ja, (640, 184), 15, art.TEXT_DIM, anchor="midtop")
        art.text(surface, f"{self.a} × {self.b} = ?", (640, 220), 40, art.GOLD, kind="display", anchor="midtop")
        field = pygame.Rect(540, 274, 200, 46)
        pygame.draw.rect(surface, (12, 18, 40), field, border_radius=10)
        pygame.draw.rect(surface, art.RED if self.wrong else art.ACCENT, field, 2, border_radius=10)
        art.text(surface, self.entry or " ", field.center, 30, art.TEXT, kind="display", anchor="center")
        if self.wrong:
            art.text(surface, i18n.t("parent_wrong"), (640, 640), 16, art.RED, anchor="midtop")
        self.buttons.draw(surface)


class ParentsScene(Scene):
    PER_PAGE = 7

    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.data = storage.load_progress()
        self.page = 0
        self.confirm = 0.0
        self.buttons = ButtonGroup([
            Button((20, 18, 150, 50), lambda: i18n.t("back"), lambda: _back(app), color=(90, 100, 140), size=20),
            Button((1000, 18, 260, 50), lambda: i18n.t("reset_confirm") if self.confirm else i18n.t("reset"),
                   self.reset, color=(150, 60, 70), size=16),
            Button((1060, 664, 70, 40), "◀", lambda: self.turn(-1), color=(60, 80, 130), size=18),
            Button((1150, 664, 70, 40), "▶", lambda: self.turn(1), color=(60, 80, 130), size=18),
        ])

    def turn(self, d):
        pages = max(1, -(-len(self.data["attempts"]) // self.PER_PAGE))
        self.page = max(0, min(pages - 1, self.page + d))

    def reset(self):
        if self.confirm > 0:
            storage.reset_progress()
            self.data = storage.load_progress()
            self.confirm = 0
            self.page = 0
        else:
            self.confirm = 3.0

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                _back(self.app)
                return
            if event.key == pygame.K_LEFT:
                self.turn(-1)
            elif event.key == pygame.K_RIGHT:
                self.turn(1)
        self.buttons.handle(event, self.app.audio)

    def update(self, dt):
        self.t += dt
        self.confirm = max(0.0, self.confirm - dt)
        self.buttons.update(self.app.mouse, dt)

    def stats(self):
        attempts = self.data["attempts"]
        solved = [a for a in attempts if a.get("result") == "solved"]
        avg = sum(a["seconds"] for a in solved) / len(solved) if solved else 0
        first = sum(1 for a in solved if a.get("wrong", 0) == 0)
        acc = 100 * first / len(solved) if solved else 0
        return solved, avg, acc

    def draw_cards(self, surface, solved, avg, acc):
        cards = [(i18n.t("games_played"), str(self.data["games"])),
                 (i18n.t("levels_solved"), str(len(solved))),
                 (i18n.t("avg_time"), f"{avg:.1f} s" if solved else "-"),
                 (i18n.t("accuracy"), f"{acc:.0f}%" if solved else "-")]
        for i, (label, value) in enumerate(cards):
            r = pygame.Rect(30 + i * 200, 86, 188, 96)
            art.panel(surface, r, radius=14, alpha=230)
            art.text(surface, label, (r.x + 14, r.y + 10), 14, art.TEXT_DIM)
            art.text(surface, value, (r.x + 14, r.y + 40), 34, art.GOLD, "display")
        r = pygame.Rect(830, 86, 420, 96)
        art.panel(surface, r, radius=14, alpha=230)
        art.text(surface, i18n.t("best_level"), (r.x + 14, r.y + 10), 14, art.TEXT_DIM)
        for j, d in enumerate(DIFFICULTIES):
            x = r.x + 14 + j * 136
            pygame.draw.rect(surface, DIFF_COLORS[d], (x, r.y + 40, 124, 44), border_radius=10)
            art.text(surface, i18n.t(d), (x + 8, r.y + 46), 13, art.TEXT)
            art.text(surface, str(self.data["best_level"].get(d, 0)), (x + 116, r.y + 52), 24, art.TEXT, "display",
                     anchor="topright")

    def draw_chart(self, surface, solved):
        box = pygame.Rect(30, 198, 1220, 196)
        art.panel(surface, box, radius=14, alpha=230)
        art.text(surface, i18n.t("chart_title"), (box.x + 16, box.y + 10), 16, art.TEXT)
        for j, d in enumerate(DIFFICULTIES):
            x = box.right - 360 + j * 120
            pygame.draw.rect(surface, DIFF_COLORS[d], (x, box.y + 14, 14, 14), border_radius=3)
            art.text(surface, i18n.t(d), (x + 20, box.y + 10), 14, art.TEXT_DIM)
        recent = solved[-40:]
        plot = pygame.Rect(box.x + 56, box.y + 44, box.w - 80, box.h - 74)
        top = 99
        for v in (0, 33, 66, 99):
            y = plot.bottom - plot.h * v / top
            pygame.draw.line(surface, (44, 54, 96), (plot.x, y), (plot.right, y), 1)
            art.text(surface, f"{v}s", (plot.x - 8, y), 12, art.TEXT_DIM, anchor="midright")
        if not recent:
            art.text(surface, i18n.t("no_attempts"), plot.center, 16, art.TEXT_DIM, anchor="center")
            return
        bw = plot.w / 40
        for i, a in enumerate(recent):
            h = max(2, plot.h * min(top, a["seconds"]) / top)
            r = pygame.Rect(int(plot.x + i * bw + 2), int(plot.bottom - h), max(2, int(bw - 4)), int(h))
            pygame.draw.rect(surface, DIFF_COLORS.get(a["difficulty"], art.ACCENT), r, border_top_left_radius=3,
                             border_top_right_radius=3)
            if bw > 22:
                art.text(surface, str(a["level"]), (r.centerx, plot.bottom + 4), 11, art.TEXT_DIM, anchor="midtop")

    def draw_table(self, surface):
        box = pygame.Rect(30, 408, 1220, 296)
        art.panel(surface, box, radius=14, alpha=230)
        art.text(surface, i18n.t("recent"), (box.x + 16, box.y + 10), 16, art.TEXT)
        cols = [("col_when", 16), ("col_diff", 190), ("col_level", 330), ("col_number", 430), ("col_result", 600),
                ("col_time", 740), ("col_wrong", 850), ("col_score", 960)]
        y = box.y + 42
        for key, x in cols:
            art.text(surface, i18n.t(key), (box.x + x, y), 14, art.GOLD)
        attempts = list(reversed(self.data["attempts"]))
        pages = max(1, -(-len(attempts) // self.PER_PAGE))
        rows = attempts[self.page * self.PER_PAGE:(self.page + 1) * self.PER_PAGE]
        if not rows:
            art.text(surface, i18n.t("no_attempts"), (box.centerx, box.y + 150), 16, art.TEXT_DIM, anchor="center")
        for i, a in enumerate(rows):
            ry = y + 28 + i * 27
            if i % 2 == 0:
                pygame.draw.rect(surface, (30, 38, 76), (box.x + 8, ry - 3, box.w - 16, 25), border_radius=5)
            result = a.get("result", "solved")
            rcolor = {"solved": art.GREEN, "timeout": art.RED}.get(result, art.TEXT_DIM)
            values = [a.get("when", ""), i18n.t(a.get("difficulty", "easy")), str(a.get("level", "")),
                      f"{a.get('target', '')}  ({a.get('bits', '')} bits)",
                      i18n.t("quit_r" if result == "quit" else result), f"{a.get('seconds', 0):.1f} s",
                      str(a.get("wrong", 0)), f"{a.get('score', 0):,}"]
            for (key, x), v in zip(cols, values):
                color = rcolor if key == "col_result" else (DIFF_COLORS.get(a.get("difficulty")) if key == "col_diff"
                                                             else art.TEXT)
                art.text(surface, v, (box.x + x, ry), 14, color)
        art.text(surface, i18n.t("page", a=self.page + 1, b=pages), (1040, 684), 14, art.TEXT_DIM, anchor="midright")

    def draw(self, surface):
        self.app.backdrop.draw(surface, self.t, fireworks=False)
        art.text(surface, f"{i18n.t('parents')}  ·  {i18n.t('progress')}", (640, 26), 28, art.TEXT, anchor="midtop",
                 shadow=True)
        solved, avg, acc = self.stats()
        self.draw_cards(surface, solved, avg, acc)
        self.draw_chart(surface, solved)
        self.draw_table(surface)
        self.buttons.draw(surface)
