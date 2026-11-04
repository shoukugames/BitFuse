"""Learn Binary: what binary is, why and where it is used, and how to count and make any number."""
import math

import pygame

from .. import art, i18n
from ..app import Scene
from ..ui import Button, ButtonGroup

AREA = pygame.Rect(790, 150, 440, 470)    # illustration area
TEXT_RECT = pygame.Rect(340, 160, 430, 470)
EXAMPLES = [13, 42, 100, 255, 7, 77]


def _back(app):
    from .title import TitleScene
    app.switch(TitleScene(app))


def switch_row(surface, values_on, center, width, height=170, labels=True, flash=None):
    """Draw a row of switches; values_on is a list of 0/1 (most significant first)."""
    n = len(values_on)
    sw = width / n
    x0 = center[0] - width / 2
    rects = []
    for i, on in enumerate(values_on):
        r = pygame.Rect(int(x0 + i * sw + 3), int(center[1] - height / 2), int(sw - 6), height)
        label = str(1 << (n - 1 - i)) if labels else None
        art.draw_switch(surface, r, float(on), label, flash=(flash[i] if flash else 0.0))
        rects.append(r)
    return rects


class IntroScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.page = 0
        self.page_t = 0.0
        self.try_bits = [0] * 8
        self.try_rects = []
        self.entries = i18n.LESSONS
        self.buttons = ButtonGroup([
            Button((24, 20, 150, 50), lambda: i18n.t("back"), lambda: _back(app), color=(90, 100, 140), size=20),
            Button((340, 640, 160, 48), lambda: i18n.t("prev"), lambda: self._select(self.page - 1),
                   color=(60, 80, 130), size=18),
            Button((1070, 640, 160, 48), lambda: i18n.t("next_page"), lambda: self._select(self.page + 1),
                   color=(52, 96, 190), size=18),
        ])
        self.nav = []
        for i, (_key, title, _body) in enumerate(self.entries):
            b = Button((24, 100 + i * 60, 282, 50), (lambda title=title: i18n.pick(title)),
                       (lambda i=i: self._select(i)), size=16)
            self.nav.append(b)
            self.buttons.add(b)
        self.clear_button = Button((AREA.centerx - 80, AREA.bottom - 20, 160, 44), lambda: i18n.t("try_clear"),
                                   self._clear_try, color=(90, 96, 130), size=17)
        self._colors()

    def _select(self, i):
        self.page = max(0, min(len(self.entries) - 1, i))
        self.page_t = 0.0
        self._colors()

    def _colors(self):
        for i, b in enumerate(self.nav):
            b.color = (220, 110, 40) if i == self.page else (44, 54, 96)

    def _clear_try(self):
        self.try_bits = [0] * 8

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                _back(self.app)
                return
            if event.key in (pygame.K_RIGHT, pygame.K_PAGEDOWN):
                self._select(self.page + 1)
                return
            if event.key in (pygame.K_LEFT, pygame.K_PAGEUP):
                self._select(self.page - 1)
                return
        if self.entries[self.page][0] == "try":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(self.try_rects):
                    if r.collidepoint(event.pos):
                        self.try_bits[i] ^= 1
                        self.app.audio.play("flip_on" if self.try_bits[i] else "flip_off")
                        return
            self.clear_button.handle(event, self.app.audio)
        self.buttons.handle(event, self.app.audio)

    def update(self, dt):
        self.t += dt
        self.page_t += dt
        self.buttons.update(self.app.mouse, dt)
        self.clear_button.update(self.app.mouse, dt)

    # ------------------------------------------------------------ illustrations
    def ill_what(self, s):
        cx, cy = AREA.centerx, AREA.centery
        on = int(self.page_t / 1.6) % 2
        for i, state in enumerate((0, 1)):
            x = cx - 110 + i * 220
            r = pygame.Rect(x - 50, cy - 150, 100, 210)
            art.draw_switch(s, r, float(state), None)
            art.text(s, i18n.t("off") if state == 0 else i18n.t("on"), (x, cy + 90), 22,
                     art.TEXT_DIM if state == 0 else art.GREEN, anchor="midtop")
        # a live bulb switched by a third, toggling switch
        bx, by = cx, cy + 180
        r = pygame.Rect(bx - 140, by - 50, 60, 120)
        art.circle(s, (40, 40, 60), (bx + 40, by), 34)
        if on:
            art.blit_glow(s, (bx + 40, by), 120, (255, 220, 120), 0.9)
            art.circle(s, (255, 240, 180), (bx + 40, by), 30)
        else:
            art.circle(s, (70, 72, 90), (bx + 40, by), 30)
        pygame.draw.rect(s, (150, 150, 160), (bx + 26, by + 26, 28, 18), border_radius=4)
        art.text(s, "1" if on else "0", (bx - 60, by), 54, art.GOLD if on else (90, 100, 140), "bold",
                 anchor="center")
        del r

    def ill_why(self, s):
        cx, cy = AREA.centerx, AREA.centery - 20
        size = 260
        chip = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        for i in range(10):  # pins
            for side in range(4):
                k = chip.x + 22 + i * 24 if side < 2 else chip.y + 22 + i * 24
                if side == 0:
                    pygame.draw.rect(s, (190, 190, 200), (k - 4, chip.y - 18, 8, 18))
                elif side == 1:
                    pygame.draw.rect(s, (190, 190, 200), (k - 4, chip.bottom, 8, 18))
                elif side == 2:
                    pygame.draw.rect(s, (190, 190, 200), (chip.x - 18, k - 4, 18, 8))
                else:
                    pygame.draw.rect(s, (190, 190, 200), (chip.right, k - 4, 18, 8))
        pygame.draw.rect(s, (30, 32, 40), chip, border_radius=12)
        pygame.draw.rect(s, (80, 84, 100), chip, 2, border_radius=12)
        cells = 10
        cs = (size - 40) / cells
        for gy in range(cells):
            for gx in range(cells):
                v = math.sin(self.t * 3 + gx * 1.7 + gy * 2.3 + math.sin(gx * gy)) > 0.1
                rr = pygame.Rect(chip.x + 20 + gx * cs + 2, chip.y + 20 + gy * cs + 2, cs - 4, cs - 4)
                pygame.draw.rect(s, (60, 220, 130) if v else (40, 50, 70), rr, border_radius=3)
        art.text(s, "Transistors" if i18n.lang() == "en" else "トランジスタ", (cx, chip.bottom + 34), 20, art.ACCENT,
                 anchor="midtop")
        bits = "".join("1" if math.sin(self.t * 5 + i) > 0 else "0" for i in range(16))
        art.text(s, bits[:8] + " " + bits[8:], (cx, chip.bottom + 70), 24, art.GOLD, "bold", anchor="midtop")
        art.text(s, "8 bits = 1 byte" if i18n.lang() == "en" else "8ビット = 1バイト", (cx, chip.bottom + 108), 18,
                 art.TEXT_DIM, anchor="midtop")

    def ill_where(self, s):
        cx = AREA.centerx
        art.text(s, "A", (cx - 150, AREA.y + 20), 90, art.TEXT, "bold", anchor="midtop", shadow=True)
        art.text(s, "→", (cx - 70, AREA.y + 50), 40, art.TEXT_DIM, anchor="midtop")
        art.text(s, "01000001", (cx + 70, AREA.y + 56), 34, art.GOLD, "bold", anchor="midtop")
        switch_row(s, [0, 1, 0, 0, 0, 0, 0, 1], (cx, AREA.y + 210), 420, 150, labels=False)
        # a tiny pixel picture: a heart, each pixel colour a number
        heart = ["01100110", "11111111", "11111111", "11111111", "01111110", "00111100", "00011000", "00000000"]
        px = 18
        ox, oy = cx - 4 * px - 100, AREA.y + 310
        for y, row in enumerate(heart):
            for x, ch in enumerate(row):
                col = (240, 70, 110) if ch == "1" else (36, 40, 70)
                pygame.draw.rect(s, col, (ox + x * px, oy + y * px, px - 2, px - 2), border_radius=2)
        art.text(s, "Pink =" if i18n.lang() == "en" else "ピンク =", (cx + 10, oy + 2), 18, (240, 70, 110))
        for i, (ch, v, col) in enumerate((("R", 240, (255, 90, 90)), ("G", 70, (90, 230, 120)),
                                          ("B", 110, (110, 150, 255)))):
            y = oy + 34 + i * 34
            art.text(s, f"{ch} {v:>3}", (cx + 10, y), 18, col, "bold")
            art.text(s, f"= {v:08b}", (cx + 80, y), 18, art.GOLD, "bold")

    def ill_important(self, s):
        cx = AREA.centerx
        en = i18n.lang() == "en"
        rows = [("1 bit", "0 / 1", "1ビット"), ("1 byte", "8 bits", "1バイト = 8ビット"),
                ("1 kilobyte (KB)", "≈ 1,000 bytes", "1キロバイト ≈ 1,000バイト"),
                ("1 megabyte (MB)", "≈ 1,000 KB", "1メガバイト ≈ 1,000KB"),
                ("1 gigabyte (GB)", "≈ 1,000 MB", "1ギガバイト ≈ 1,000MB")]
        for i, (a, b, ja) in enumerate(rows):
            y = AREA.y + 10 + i * 88
            w = 180 + i * 60
            r = pygame.Rect(cx - w // 2, y, w, 72)
            k = 0.5 + 0.5 * math.sin(self.t * 2 - i * 0.7)
            col = art.mix((40, 60, 130), (90, 60, 170), i / 4)
            art.panel(s, r, color=col, border=art.mix(art.EDGE, art.GOLD, k * 0.6), radius=14, alpha=240)
            if en:
                art.text(s, a, (r.centerx, r.y + 10), 20, art.TEXT, anchor="midtop")
                art.text(s, b, (r.centerx, r.y + 40), 16, art.GOLD, anchor="midtop")
            else:
                art.text(s, ja, r.center, 18, art.TEXT, anchor="center")

    def ill_count(self, s):
        cx, cy = AREA.centerx, AREA.y + 150
        n = int(self.page_t / 1.1) % 16
        bits = [(n >> (3 - i)) & 1 for i in range(4)]
        switch_row(s, bits, (cx, cy), 400, 210)
        art.text(s, "".join(map(str, bits)), (cx, cy + 140), 50, art.GOLD, "bold", anchor="midtop", shadow=True)
        art.text(s, f"= {n}", (cx, cy + 210), 46, art.TEXT, "bold", anchor="midtop")
        # a little table of the first numbers, the current one lit
        for k in range(16):
            x = AREA.x + 20 + (k % 8) * 52
            y = AREA.bottom - 80 + (k // 8) * 34
            art.text(s, f"{k}", (x + 22, y), 18, art.GOLD if k == n else art.TEXT_DIM, "bold", anchor="midtop")

    def ill_place(self, s):
        cx = AREA.centerx
        bits = [1, 0, 1, 1]
        rects = switch_row(s, bits, (cx, AREA.y + 120), 400, 200)
        for a, b in zip(rects, rects[1:]):
            art.text(s, "×2", ((a.centerx + b.centerx) // 2, a.y - 22), 16, art.ACCENT, anchor="center")
        art.text(s, "1011", (cx, AREA.y + 250), 44, art.GOLD, "bold", anchor="midtop")
        art.text(s, "8 + 0 + 2 + 1 = 11", (cx, AREA.y + 310), 30, art.TEXT, "bold", anchor="midtop")
        vals = [128, 64, 32, 16, 8, 4, 2, 1]
        for i, v in enumerate(vals):
            k = 0.5 + 0.5 * math.sin(self.t * 3 - i * 0.6)
            art.text(s, str(v), (AREA.x + 30 + i * 54, AREA.y + 390), 20, art.mix(art.TEXT_DIM, art.GOLD, k),
                     "bold", anchor="midtop")

    def ill_make(self, s):
        cx = AREA.centerx
        period = 9.0
        ex = EXAMPLES[int(self.page_t / period) % len(EXAMPLES)]
        local = self.page_t % period
        nbits = 4 if ex < 16 else 8
        step = int(local / 0.9)
        remaining = ex
        bits = [0] * nbits
        lines = []
        for i in range(nbits):
            v = 1 << (nbits - 1 - i)
            if i >= step:
                break
            if v <= remaining:
                bits[i] = 1
                lines.append((f"{v} ≤ {remaining}  →  ON    {remaining} − {v} = {remaining - v}", art.GREEN))
                remaining -= v
            else:
                lines.append((f"{v} > {remaining}  →  OFF", art.TEXT_DIM))
        art.text(s, f"{ex}", (cx, AREA.y - 10), 54, art.GOLD, "bold", anchor="midtop", shadow=True)
        switch_row(s, bits, (cx, AREA.y + 150), 440 if nbits == 8 else 300, 160)
        for i, (line, color) in enumerate(lines):
            art.text(s, line, (AREA.x + 10, AREA.y + 250 + i * 27), 19, color, "bold")
        if step >= nbits:
            art.text(s, f"{ex} = " + "".join(map(str, bits)), (cx, AREA.bottom - 18), 30, art.ORANGE, "bold",
                     anchor="midbottom")

    def ill_try(self, s):
        cx = AREA.centerx
        self.try_rects = switch_row(s, self.try_bits, (cx, AREA.y + 120), 440, 210)
        total = sum(1 << (7 - i) for i, b in enumerate(self.try_bits) if b)
        art.text(s, i18n.t("try_total"), (cx, AREA.y + 250), 20, art.TEXT_DIM, anchor="midtop")
        art.text(s, "".join(map(str, self.try_bits)), (cx, AREA.y + 282), 34, art.GOLD, "bold", anchor="midtop")
        art.text(s, f"= {total}", (cx, AREA.y + 330), 56, art.TEXT, "bold", anchor="midtop", shadow=True)
        self.clear_button.draw(s)

    def ill_howto(self, s):
        cx, cy = AREA.centerx, AREA.y + 40
        box = pygame.Rect(cx - 90, cy - 20, 180, 80)
        art.panel(s, box, color=(16, 18, 46), border=(255, 170, 70), radius=16)
        art.text(s, "5", box.center, 52, art.GOLD, "bold", anchor="center")
        rects = switch_row(s, [1, 0, 1], (cx, cy + 210), 300, 190)
        fy = art.switch_layout(rects[0])["fuse_y"]
        x1, x2 = rects[0].x - 20, rects[-1].right + 20
        ground = AREA.bottom - 10
        art.aaline(s, art.FUSE, (x1, fy), (x2, fy), 5)
        art.aaline(s, art.FUSE, (x2, fy), (x2, ground), 5)
        art.aaline(s, art.FUSE, (x2, ground), (cx - 100, ground), 5)
        art.draw_mortar(s, (cx - 100, ground + 4), 60, 28, (170, 40, 50))
        # the spark runs along it
        total = (x2 - x1) + (ground - fy) + (x2 - cx + 100)
        d = (self.page_t * 260) % (total + 200)
        if d < x2 - x1:
            p = (x1 + d, fy)
        elif d < x2 - x1 + ground - fy:
            p = (x2, fy + d - (x2 - x1))
        elif d < total:
            p = (x2 - (d - (x2 - x1) - (ground - fy)), ground)
        else:
            p = None
            k = (d - total) / 200
            art.blit_glow(s, (cx - 100, ground - 260 * k), 60, (255, 140, 200), 1 - k)
        if p:
            art.blit_glow(s, p, 30, (255, 160, 60), 1.0)
            art.blit_glow(s, p, 8, (255, 255, 230), 1.0)
        art.text(s, "4 + 1 = 5", (cx + 120, ground - 40), 24, art.GREEN, "bold", anchor="center")

    def draw(self, surface):
        self.app.backdrop.draw(surface, self.t, fireworks=False)
        art.text(surface, i18n.t("intro_title"), (200, 28), 30, art.GOLD, shadow=True)
        art.panel(surface, (320, 90, 930, 610), radius=22, alpha=230)
        key, title, body = self.entries[self.page]
        art.text(surface, i18n.pick(title), (345, 106), 30, art.TEXT, shadow=True)
        pygame.draw.line(surface, (90, 110, 190), (345, 148), (1220, 148), 2)
        art.paragraph(surface, i18n.pick(body), TEXT_RECT.move(0, 8), 17, art.TEXT, spacing=1.4)
        getattr(self, "ill_" + key)(surface)
        art.text(surface, f"{self.page + 1} / {len(self.entries)}", (785, 664), 18, art.TEXT_DIM, anchor="center")
        self.buttons.draw(surface)
