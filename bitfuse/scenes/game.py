"""The game: flick the switches to make the number, ignite the fuse, enjoy the show.

States
    brief    level card before the clock starts
    play     the clock runs and the switches can be flicked
    burn     the spark runs along the fuse (clock stopped)
    show     the fireworks show for a solved level
    over     time ran out or the player quit: score and name entry
    victory  all 100 levels solved
"""
import math
import random

import pygame

from .. import art, i18n, levels, storage
from ..app import H, W, Scene
from ..fireworks import PALETTES, Fireworks, prewarm
from ..fuse import Fuse
from ..ui import Button, ButtonGroup, Toast, overlay

GROUND = H - 16
BANK_TOP = 258
SLOT_H = 206
SPARK_SPEED = 820.0
DIFF_COLORS = {"easy": (40, 160, 90), "medium": (200, 140, 30), "hard": (200, 60, 70)}
MORTAR_COLORS = [(170, 40, 50), (40, 90, 170), (40, 140, 80), (150, 70, 160), (190, 120, 30)]


class GameScene(Scene):
    music = "game"

    def __init__(self, app, difficulty, seed=None, start_level=1):
        super().__init__(app)
        self.difficulty = difficulty
        self.rng = random.Random(seed)
        self.t = 0.0
        self.score = 0
        self.shown_score = 0.0
        self.number = start_level
        self.level = None
        self.previous = None
        self.state = "brief"
        self.paused = False
        self.toast = Toast()
        prewarm()
        self.fx = Fireworks((W, H), sound=self._fx_sound, seed=seed)
        self.sparks = []
        self.popups = []
        self.name = app.settings.get("last_name", "")
        self.rank = None
        self.saved = False
        self.result_text = ""
        self.sel = 0
        self.hover_i = -1
        self.wrong = 0
        self.elapsed = 0.0
        self.time_left = float(levels.TIME_LIMIT)
        self.penalty_flash = 0.0
        self.last_tick = None
        self.bonus = 0
        storage.record_game_start()
        self._build_buttons()
        self.new_level()

    # ------------------------------------------------------------ set-up
    def _build_buttons(self):
        self.play_buttons = ButtonGroup([
            Button((W // 2 - 140, 556, 280, 64), lambda: i18n.t("ignite"), self.ignite, color=(214, 70, 30),
                   size=30, kind="bold"),
            Button((W - 150, 12, 132, 44), lambda: i18n.t("menu"), self.pause, color=(70, 80, 130), size=18),
        ])
        self.brief_buttons = ButtonGroup([
            Button((W // 2 - 130, 470, 260, 62), lambda: i18n.t("start"), self.start_level, color=(40, 160, 90),
                   size=28),
        ])
        self.pause_buttons = ButtonGroup([
            Button((W // 2 - 150, 330, 300, 60), lambda: i18n.t("resume"), self.resume, color=(40, 160, 90), size=24),
            Button((W // 2 - 150, 410, 300, 60), lambda: i18n.t("to_title"), self.quit_to_title,
                   color=(150, 60, 70), size=22),
        ])
        self.over_buttons = ButtonGroup([
            Button((W // 2 - 290, 560, 270, 58), lambda: i18n.t("retry"), self.retry, color=(220, 110, 40), size=22),
            Button((W // 2 + 20, 560, 270, 58), lambda: i18n.t("to_title"), self.finish, color=(70, 80, 130),
                   size=22),
        ])
        self.save_button = Button((W // 2 + 170, 470, 120, 50), lambda: i18n.t("save"), self.save_score,
                                  color=(40, 160, 90), size=20)

    def new_level(self):
        self.level = levels.generate(self.number, self.difficulty, self.rng, self.previous)
        self.previous = self.level.target
        self.states = list(self.level.start)
        self.pos = [float(s) for s in self.states]
        self.flash = [0.0] * self.level.bits
        self.sel = self.level.bits - 1
        self.time_left = float(levels.TIME_LIMIT)
        self.elapsed = 0.0
        self.wrong = 0
        self.burn = 0.0
        self.correct = False
        self.passed = set()
        self.lit_mortars = set()
        self.running_total = 0
        self.notes_played = 0
        self.show = levels.show_plan(self.number, random.Random(self.rng.random()))
        self.show_clock = 0.0
        self.show_index = 0
        self.state = "brief"
        self.brief_t = 0.0
        self.last_tick = None
        self._layout()

    def _layout(self):
        n = self.level.bits
        sw = min(118, (W - 110) // n)
        bank_w = sw * n
        x0 = (W - bank_w) // 2
        self.slots = [pygame.Rect(x0 + i * sw + 4, BANK_TOP, sw - 8, SLOT_H) for i in range(n)]
        self.bank = pygame.Rect(x0 - 26, BANK_TOP - 18, bank_w + 52, SLOT_H + 48)
        fy = art.switch_layout(self.slots[0])["fuse_y"]
        left = self.bank.left + 6
        right = min(W - 22, self.bank.right + 8)
        pts = [(left, fy)]
        pts.append((self.bank.right - 8, fy))
        # sweep down the right side to the ground, then along to the mortars
        p0, p1, p2, p3 = (self.bank.right - 8, fy), (right + 6, fy), (right + 6, GROUND - 40), (right - 50, GROUND)
        for i in range(1, 21):
            k = i / 20
            a = (1 - k) ** 3
            b = 3 * (1 - k) ** 2 * k
            c = 3 * (1 - k) * k ** 2
            d = k ** 3
            pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
        m = self.show["mortars"]
        span_left, span_right = 90, right - 110
        if m == 1:
            self.mortar_x = [W // 2]
        else:
            self.mortar_x = [span_right - i * (span_right - span_left) / (m - 1) for i in range(m)]
        pts.append((min(self.mortar_x) - 30, GROUND))
        self.fuse = Fuse(pts, (W, H))
        self.igniter = (left - 8, fy)
        self.switch_marks = [self.fuse.distance_to_x(s.centerx, fy) for s in self.slots]
        self.bank_end = self.fuse.distance_to_x(self.bank.right - 10, fy)
        self.mortar_marks = [self.fuse.distance_to_x(x, GROUND) for x in self.mortar_x]
        rng = random.Random(self.number)
        self.mortar_look = [(rng.randint(44, 64) + self.number // 6, rng.randint(22, 30), rng.choice(MORTAR_COLORS))
                            for _ in range(m)]
        self.mortar_flash = [0.0] * m

    # ------------------------------------------------------------ actions
    def start_level(self):
        if self.state != "brief":
            return
        self.state = "play"
        self.app.audio.play("start")

    def toggle(self, i):
        if self.state != "play" or self.paused or not (0 <= i < self.level.bits):
            return
        self.states[i] = 0 if self.states[i] else 1
        self.sel = i
        self.app.audio.play("flip_on" if self.states[i] else "flip_off", self._pan(self.slots[i].centerx))

    def value(self):
        return levels.from_bits(self.states)

    def ignite(self):
        if self.state != "play" or self.paused:
            return
        self.correct = self.value() == self.level.target
        self.state = "burn"
        self.burn = 0.0
        self.passed = set()
        self.running_total = 0
        self.notes_played = 0
        self.app.audio.play("ignite")
        self.app.audio.loop("sizzle", True)
        if self.correct:
            self.bonus = levels.score_for(self.time_left)

    def _fizzle(self):
        self.app.audio.loop("sizzle", False)
        self.app.audio.play("wrong")
        self.wrong += 1
        v, target = self.value(), self.level.target
        if self.level.show_total or self.difficulty == "medium":
            msg = i18n.t("wrong_total", v=v, t=target)
        else:
            msg = i18n.t("wrong_high") if v > target else i18n.t("wrong_low")
        self.toast.show(msg, art.RED, 4.0)
        self.time_left = max(0.0, self.time_left - self.level.penalty)
        self.penalty_flash = 1.2
        (x, y), _ = self.fuse.at(self.burn)
        for _ in range(30):
            self.sparks.append([x, y, random.uniform(-90, 90), random.uniform(-160, 20), random.uniform(0.3, 0.8),
                                (140, 140, 150)])
        self.burn = 0.0
        if self.time_left <= 0:
            self.game_over("timeout")
        else:
            self.state = "play"

    def _success(self):
        self.app.audio.play("fanfare")
        self.app.audio.duck(True)
        self.score += self.bonus

    def after_show(self):
        """The show is over (or skipped): record the level and move on."""
        if self.state != "show":
            return
        storage.record_attempt(self.number, self.difficulty, self.level.target, self.level.bits, "solved",
                               self.elapsed, self.wrong, self.bonus)
        self.app.audio.duck(False)
        if self.number >= levels.LEVELS:
            self.state = "victory"
            self.app.audio.stop_music_fx()
            self.app.audio.play("victory")
            self.app.audio.duck(True)
            self._prepare_over()
            return
        self.number += 1
        self.new_level()

    def pause(self):
        if self.state in ("play", "brief", "burn", "show"):
            self.paused = True
            self.app.audio.loop("sizzle", False)

    def resume(self):
        self.paused = False
        if self.state == "burn":
            self.app.audio.loop("sizzle", True)

    def quit_to_title(self):
        self.paused = False
        if self.state == "show":
            storage.record_attempt(self.number, self.difficulty, self.level.target, self.level.bits, "solved",
                                   self.elapsed, self.wrong, self.bonus)
        self.game_over("quit")

    def game_over(self, why):
        self.app.audio.loop("sizzle", False)
        self.app.audio.stop_music_fx()
        self.app.audio.duck(False)
        if why == "timeout":
            self.app.audio.play("time_up")
        if self.state in ("play", "burn"):
            storage.record_attempt(self.number, self.difficulty, self.level.target, self.level.bits, why,
                                   self.elapsed, self.wrong, 0)
        self.why = why
        self.state = "over"
        self._prepare_over()

    def _prepare_over(self):
        self.rank = None
        self.saved = False
        self.qualifies = storage.qualifies(self.score)
        if self.qualifies:
            self.app.audio.play("new_record")
            pygame.key.start_text_input()

    def save_score(self):
        if not self.qualifies or self.saved:
            return
        name = self.name.strip() or "PLAYER"
        self.rank = storage.add_score(name, self.score, self.number, self.difficulty)
        self.app.settings["last_name"] = name
        self.app.save()
        self.saved = True
        pygame.key.stop_text_input()
        self.app.audio.play("click")

    def retry(self):
        self.save_score()
        self.app.audio.stop_music_fx()
        self.app.audio.duck(False)
        self.app.switch(GameScene(self.app, self.difficulty))

    def finish(self):
        self.save_score()
        self.app.audio.stop_music_fx()
        self.app.audio.duck(False)
        from .title import TitleScene
        self.app.switch(TitleScene(self.app))

    def leave(self):
        self.app.audio.loop("sizzle", False)
        pygame.key.stop_text_input()

    # ------------------------------------------------------------ input
    def _slot_at(self, pos):
        for i, r in enumerate(self.slots):
            if r.inflate(6, 10).collidepoint(pos):
                return i
        return -1

    def handle(self, event):
        audio = self.app.audio
        if self.paused:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.resume()
                return
            self.pause_buttons.handle(event, audio)
            return
        if self.state in ("over", "victory"):
            if self.qualifies and not self.saved:
                if event.type == pygame.TEXTINPUT:
                    if len(self.name) < 12:
                        self.name += event.text
                    self.name = self.name[:12]
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.save_score()
                    return
                self.save_button.handle(event, audio)
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.retry()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.finish()
                return
            self.over_buttons.handle(event, audio)
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause()
            return
        if self.state == "brief":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.start_level()
                return
            self.brief_buttons.handle(event, audio)
            self.play_buttons.buttons[1].handle(event, audio)
            return
        if self.state == "show":
            if self.show_clock > 1.5 and (
                    (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or
                    (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE,
                                                                    pygame.K_KP_ENTER))):
                if not self.play_buttons.buttons[1].rect.collidepoint(getattr(event, "pos", (-1, -1))):
                    self.after_show()
                    return
            self.play_buttons.buttons[1].handle(event, audio)
            return
        if self.state != "play":
            self.play_buttons.buttons[1].handle(event, audio)
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.sel = max(0, self.sel - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.sel = min(self.level.bits - 1, self.sel + 1)
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                if event.key in (pygame.K_UP, pygame.K_w) and self.states[self.sel]:
                    return
                if event.key in (pygame.K_DOWN, pygame.K_s) and not self.states[self.sel]:
                    return
                self.toggle(self.sel)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.ignite()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            i = self._slot_at(event.pos)
            if i >= 0:
                self.toggle(i)
                return
        self.play_buttons.handle(event, audio)

    # ------------------------------------------------------------ update
    def _pan(self, x):
        return max(-1.0, min(1.0, x / W * 2 - 1)) * 0.7

    def _fx_sound(self, name, pan=0.0):
        self.app.audio.play(name, pan)

    def _launch(self, m, kind=None, scale=None):
        x = self.mortar_x[m]
        h = self.mortar_look[m][0]
        kind = kind or random.choice([k for lv, k in levels.SHELL_UNLOCKS if self.number >= lv])
        scale = scale or self.show["size"]
        self.fx.launch(x, GROUND - h, kind, scale, random.choice(PALETTES),
                       apex=random.uniform(70, 300 - 120 * min(1.0, scale - 0.6)))
        self.mortar_flash[m] = 1.0

    def update(self, dt):
        self.t += dt
        self.toast.update(dt)
        self.penalty_flash = max(0.0, self.penalty_flash - dt)
        self.shown_score += (self.score - self.shown_score) * min(1.0, dt * 4)
        if abs(self.score - self.shown_score) < 1:
            self.shown_score = self.score
        mouse = self.app.mouse
        for i in range(len(self.pos)):
            target = float(self.states[i])
            self.pos[i] += (target - self.pos[i]) * min(1.0, dt * 22)
            self.flash[i] = max(0.0, self.flash[i] - dt * 1.6)
        for i in range(len(self.mortar_flash)):
            self.mortar_flash[i] = max(0.0, self.mortar_flash[i] - dt * 2.5)
        self.fx.update(dt)
        self._update_sparks(dt)
        for p in self.popups:
            p[1] -= dt * 14
            p[4] -= dt
        self.popups = [p for p in self.popups if p[4] > 0]
        if self.paused:
            self.pause_buttons.update(mouse, dt)
            return
        if self.state == "brief":
            self.brief_t += dt
            self.brief_buttons.update(mouse, dt)
            self.play_buttons.buttons[1].update(mouse, dt)
        elif self.state == "play":
            self.hover_i = self._slot_at(mouse)
            self.play_buttons.update(mouse, dt)
            self.elapsed += dt
            self.time_left -= dt
            sec = math.ceil(self.time_left)
            if sec <= 10 and sec != self.last_tick and sec > 0:
                self.last_tick = sec
                self.app.audio.play("tick")
            if self.time_left <= 0:
                self.time_left = 0
                self.game_over("timeout")
        elif self.state == "burn":
            self.play_buttons.buttons[1].update(mouse, dt)
            self._update_burn(dt)
        elif self.state == "show":
            self.play_buttons.buttons[1].update(mouse, dt)
            self._update_show(dt)
        elif self.state in ("over", "victory"):
            self.over_buttons.update(mouse, dt)
            self.save_button.update(mouse, dt)
            if self.state == "victory" and random.random() < dt * 2.2:
                self._launch(random.randrange(len(self.mortar_x)), scale=random.uniform(1.2, 1.7))

    def _emit(self, x, y, n=3):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            s = random.uniform(40, 170)
            self.sparks.append([x, y, math.cos(a) * s, math.sin(a) * s - 40, random.uniform(0.15, 0.45),
                                random.choice([(255, 200, 90), (255, 150, 40), (255, 240, 200)])])

    def _update_sparks(self, dt):
        for s in self.sparks:
            s[0] += s[2] * dt
            s[1] += s[3] * dt
            s[3] += 300 * dt
            s[4] -= dt
        self.sparks = [s for s in self.sparks if s[4] > 0][-500:]

    def _update_burn(self, dt):
        speed = SPARK_SPEED * (1.25 if self.burn > self.bank_end else 1.0)
        self.burn += speed * dt
        (x, y), _ = self.fuse.at(self.burn)
        self._emit(x, y, 4)
        for i, mark in enumerate(self.switch_marks):
            if i not in self.passed and self.burn >= mark:
                self.passed.add(i)
                if self.states[i]:
                    value = 1 << (self.level.bits - 1 - i)
                    self.running_total += value
                    self.flash[i] = 1.0
                    self.app.audio.play(f"bit{min(15, self.notes_played):02d}", self._pan(self.slots[i].centerx))
                    self.notes_played += 1
                    self.popups.append([self.slots[i].centerx, self.slots[i].y - 6, f"+{value}", art.GOLD, 1.2,
                                        18 if value < 1000 else 15])
        if self.burn >= self.bank_end and not self.correct:
            self._fizzle()
            return
        if self.burn >= self.bank_end and self.correct and "won" not in self.passed:
            self.passed.add("won")
            self._success()
        for m, mark in enumerate(self.mortar_marks):
            if m not in self.lit_mortars and self.burn >= mark:
                self.lit_mortars.add(m)
                self.app.audio.play("mortar", self._pan(self.mortar_x[m]))
                self._launch(m)
        if self.burn >= self.fuse.length:
            self.app.audio.loop("sizzle", False)
            self.state = "show"
            self.show_clock = 0.0
            self.show_index = 0

    def _update_show(self, dt):
        self.show_clock += dt
        plan = self.show["plan"]
        while self.show_index < len(plan) and plan[self.show_index][0] <= self.show_clock:
            _t, m, kind, scale = plan[self.show_index]
            self._launch(m, kind, scale)
            self.show_index += 1
        if self.show_clock >= self.show["duration"] and self.show_index >= len(plan):
            self.after_show()

    # ------------------------------------------------------------ drawing
    def draw_hud(self, surface):
        bar = pygame.Rect(0, 0, W, 66)
        art.panel(surface, bar.inflate(0, 0), radius=0, alpha=200, shadow=False, border=None)
        pygame.draw.line(surface, (80, 100, 180), (0, 66), (W, 66), 2)
        art.text(surface, i18n.t("level"), (24, 8), 15, art.TEXT_DIM)
        art.text(surface, f"{self.number}", (24, 26), 30, art.TEXT, "display")
        art.text(surface, f"/ {levels.LEVELS}", (24 + art.render(str(self.number), 30, art.TEXT, "display")
                                                .get_width() + 8, 38), 16, art.TEXT_DIM, "display")
        badge = pygame.Rect(170, 20, 120, 30)
        pygame.draw.rect(surface, DIFF_COLORS[self.difficulty], badge, border_radius=15)
        art.text(surface, i18n.t(self.difficulty), badge.center, 16, art.TEXT, anchor="center")
        art.text(surface, i18n.t("score"), (330, 8), 15, art.TEXT_DIM)
        art.text(surface, f"{int(self.shown_score):,}", (330, 26), 30, art.GOLD, "display")
        # timer: a ring that empties
        cx, cy, r = W - 230, 34, 27
        frac = max(0.0, self.time_left / levels.TIME_LIMIT)
        low = self.time_left <= 10
        color = art.RED if low else (art.ORANGE if self.time_left <= 30 else art.ACCENT)
        art.circle(surface, (20, 24, 50), (cx, cy), r + 4)
        pygame.draw.circle(surface, (50, 60, 100), (cx, cy), r, 5)
        if frac > 0:
            rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            pygame.draw.arc(surface, color, rect, math.pi / 2, math.pi / 2 + math.tau * frac, 6)
        if low and self.state == "play":
            art.blit_glow(surface, (cx, cy), 50, (255, 60, 60), 0.4 + 0.3 * math.sin(self.t * 10))
        art.text(surface, f"{math.ceil(self.time_left)}", (cx, cy + 1), 22, color, "display", anchor="center")
        art.text(surface, i18n.t("time"), (cx - 40, cy), 15, art.TEXT_DIM, anchor="midright")
        if self.penalty_flash > 0:
            art.text(surface, i18n.t("penalty", s=self.level.penalty), (cx, cy + 40 + (1.2 - self.penalty_flash) * 20),
                     22, art.RED, "bold", anchor="midtop", shadow=True, alpha=int(255 * min(1, self.penalty_flash)))

    def draw_target(self, surface):
        box = pygame.Rect(W // 2 - 300, 78, 600, 150)
        art.panel(surface, box, color=(16, 18, 46), border=(255, 170, 70), radius=22, alpha=225)
        if self.state == "show" or (self.state == "burn" and "won" in self.passed):
            art.text(surface, i18n.t("correct"), (box.centerx, box.y + 8), 30, art.GREEN, anchor="midtop", shadow=True)
            answer = "".join(map(str, self.level.answer))
            num = art.gradient_text(f"{self.level.target} = {answer}", 58, (255, 245, 190), (255, 140, 40),
                                    kind="bold", outline=(60, 20, 0))
            if num.get_width() > box.w - 36:
                k = (box.w - 36) / num.get_width()
                num = pygame.transform.smoothscale(num, (int(num.get_width() * k), int(num.get_height() * k)))
            surface.blit(num, num.get_rect(center=(box.centerx, box.y + 84)))
            art.text(surface, i18n.t("bonus", s=int(self.time_left), p=f"{self.bonus:,}"),
                     (box.centerx, box.bottom - 12), 18, art.GOLD, anchor="midbottom")
            return
        art.text(surface, i18n.t("make"), (box.centerx, box.y + 12), 18, art.TEXT_DIM, anchor="midtop")
        num = art.gradient_text(str(self.level.target), 92, (255, 245, 190), (255, 140, 40), kind="bold",
                                outline=(60, 20, 0))
        pulse = 0.5 + 0.5 * math.sin(self.t * 2.4)
        art.blit_glow(surface, (box.centerx, box.y + 92), 160, (110, 50, 10), 0.3 + 0.2 * pulse)
        surface.blit(num, num.get_rect(center=(box.centerx, box.y + 92)))

    def draw_bank(self, surface):
        art.panel(surface, self.bank, color=(26, 30, 56), border=(110, 120, 170), radius=20, alpha=235)
        for x in (self.bank.left + 12, self.bank.right - 12):
            for y in (self.bank.top + 12, self.bank.bottom - 12):
                art.circle(surface, (70, 76, 100), (x, y), 5)
                art.circle(surface, (130, 136, 160), (x - 1, y - 1), 3)
        show_values = self.level.show_values
        n = self.level.bits
        for i, r in enumerate(self.slots):
            value = 1 << (n - 1 - i)
            label = str(value) if show_values else "?"
            draw_hover = 1.0 if (i == self.hover_i and self.state == "play") else 0.0
            art.draw_switch(surface, r, self.pos[i], label, selected=(i == self.sel and self.state == "play"),
                            hover=draw_hover, flash=self.flash[i])

    def draw_ground(self, surface):
        for m, x in enumerate(self.mortar_x):
            h, w, color = self.mortar_look[m]
            art.draw_mortar(surface, (x, GROUND + 4), h, w, color, self.mortar_flash[m])

    def draw_fuse(self, surface):
        burnt = self.burn if self.state == "burn" else (self.fuse.length if self.state == "show" else 0.0)
        self.fuse.draw(surface, burnt, self.t)

    def _draw_spark(self, surface):
        # the igniter cap at the start of the fuse
        ix, iy = self.igniter
        pygame.draw.rect(surface, (90, 70, 40), (ix - 14, iy - 12, 18, 24), border_radius=5)
        pygame.draw.rect(surface, art.BRASS, (ix - 14, iy - 12, 18, 24), 2, border_radius=5)
        if self.state == "burn":
            (x, y), _ = self.fuse.at(self.burn)
            flick = 0.8 + 0.2 * math.sin(self.t * 50)
            art.blit_glow(surface, (x, y), 46, (255, 150, 40), flick)
            art.blit_glow(surface, (x, y), 14, (255, 255, 230), 1.0)

    def draw_sparks(self, surface):
        for x, y, _vx, _vy, life, color in self.sparks:
            k = min(1.0, life * 3)
            art.blit_glow(surface, (x, y), 5, color, round(k, 1))

    def draw_total(self, surface):
        y = 520
        if self.state == "burn":
            txt = f"= {self.running_total}"
            art.text(surface, txt, (W // 2, y), 30, art.GOLD, "bold", anchor="midtop", shadow=True)
            return
        if self.state != "play" or not self.level.show_total:
            return
        n = self.level.bits
        on = [1 << (n - 1 - i) for i, s in enumerate(self.states) if s]
        total = sum(on)
        formula = " + ".join(str(v) for v in on) if on else "0"
        if len(on) > 1:
            formula += f" = {total}"
        color = art.GREEN if total == self.level.target else art.TEXT
        art.text(surface, f"{i18n.t('total')}:  {formula}", (W // 2, y), 22, color, anchor="midtop", shadow=True)

    def draw_brief(self, surface):
        overlay(surface, 120)
        box = pygame.Rect(W // 2 - 330, 150, 660, 410)
        art.panel(surface, box, radius=26, alpha=245)
        img = art.gradient_text(i18n.t("level_intro", n=self.number), 60, (255, 240, 170), (255, 130, 40),
                                kind="display", outline=(50, 20, 0))
        surface.blit(img, img.get_rect(midtop=(box.centerx, box.y + 26)))
        art.text(surface, i18n.t("level_bits", b=self.level.bits), (box.centerx, box.y + 116), 24, art.ACCENT,
                 anchor="midtop")
        hints = []
        r = levels.RULES[self.difficulty]
        if self.number == 1:
            hints.append(i18n.t("level_hint_values"))
        if not self.level.show_values and self.number == r["values_until"] + 1:
            hints.append(i18n.t("level_hint_hidden"))
        if r["scramble_from"] is not None and self.number == r["scramble_from"]:
            hints.append(i18n.t("level_hint_scramble"))
        y = box.y + 162
        for h in hints:
            y = art.paragraph(surface, h, (box.x + 50, y, box.w - 100, 80), 19, art.GOLD, align="center") + 8
        art.paragraph(surface, i18n.t("controls"), (box.x + 50, max(y, box.y + 250), box.w - 100, 60), 15,
                      art.TEXT_DIM, align="center")
        self.brief_buttons.draw(surface)

    def draw_over(self, surface):
        overlay(surface, 60 if self.state == "victory" else 150)
        box = pygame.Rect(W // 2 - 330, 110, 660, 530)
        art.panel(surface, box, radius=26, alpha=245)
        if self.state == "victory":
            title = i18n.t("victory")
            img = art.gradient_text(title, 40, (255, 250, 200), (255, 160, 60), kind="bold", outline=(50, 20, 0))
        else:
            title = i18n.t("time_up") if getattr(self, "why", "") == "timeout" else i18n.t("game_over")
            img = art.gradient_text(title, 56, (255, 200, 200), (255, 80, 80), kind="display", outline=(50, 0, 0))
        surface.blit(img, img.get_rect(midtop=(box.centerx, box.y + 26)))
        art.text(surface, i18n.t("final_score"), (box.centerx, box.y + 120), 22, art.TEXT_DIM, anchor="midtop")
        art.text(surface, f"{self.score:,}", (box.centerx, box.y + 150), 64, art.GOLD, "display", anchor="midtop",
                 shadow=True)
        art.text(surface, i18n.t("reached", n=self.number, d=i18n.t(self.difficulty)), (box.centerx, box.y + 238),
                 20, art.TEXT, anchor="midtop")
        if self.qualifies and not self.saved:
            art.text(surface, i18n.t("new_high"), (box.centerx, box.y + 300), 20, art.GREEN, anchor="midtop")
            field = pygame.Rect(W // 2 - 290, 470, 440, 50)
            pygame.draw.rect(surface, (10, 14, 36), field, border_radius=10)
            pygame.draw.rect(surface, art.ACCENT, field, 2, border_radius=10)
            caret = "|" if int(self.t * 2) % 2 == 0 else ""
            art.text(surface, self.name + caret, (field.x + 16, field.centery), 26, art.TEXT, anchor="midleft")
            self.save_button.draw(surface)
        elif self.saved and self.rank is not None and self.rank >= 0:
            art.text(surface, f"#{self.rank + 1}  {self.name or 'PLAYER'}", (box.centerx, box.y + 320), 30,
                     art.GREEN, anchor="midtop")
        self.over_buttons.draw(surface)

    def draw(self, surface):
        self.app.backdrop.draw(surface, self.t, fireworks=False)
        self.draw_ground(surface)
        self.draw_hud(surface)
        self.draw_target(surface)
        self.draw_bank(surface)
        # the fuse runs through the bottom of the switch bank, drawn above the panel
        self.draw_fuse(surface)
        self._draw_spark(surface)
        self.draw_sparks(surface)
        self.draw_total(surface)
        # fireworks light up over everything
        self.fx.draw(surface, 196)
        if self.state == "play":
            self.play_buttons.draw(surface)
        else:
            self.play_buttons.buttons[1].draw(surface)
        for x, y, txt, color, life, size in self.popups:
            art.text(surface, txt, (x, y), size, color, "bold", anchor="center", shadow=True,
                     alpha=int(255 * min(1.0, life)))
        if self.state == "show" and self.show_clock > 1.5:
            k = 0.5 + 0.5 * math.sin(self.t * 4)
            art.text(surface, i18n.t("skip"), (W // 2, 590), 18, art.mix(art.TEXT_DIM, art.TEXT, k), anchor="center",
                     shadow=True)
        self.toast.draw(surface, (W // 2 - 320, 628, 640, 56), 18)
        if self.state == "brief":
            self.draw_brief(surface)
        elif self.state in ("over", "victory"):
            self.draw_over(surface)
        if self.paused:
            overlay(surface, 170)
            img = art.gradient_text(i18n.t("paused"), 56, (220, 235, 255), (110, 160, 255), kind="display",
                                    outline=(10, 20, 50))
            surface.blit(img, img.get_rect(midtop=(W // 2, 210)))
            self.pause_buttons.draw(surface)
