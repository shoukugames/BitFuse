"""All drawing: fonts, panels, glows, the night sky, toggle switches, fuse and mortars.

Everything is drawn with pygame at run time - there are no image files apart
from the icon. Static pictures are cached.
"""
import math
import random

import pygame
import pygame.gfxdraw

from .paths import asset

# Palette
BG_TOP = (6, 8, 30)
BG_BOTTOM = (40, 22, 70)
PANEL = (20, 26, 58)
PANEL_LIGHT = (34, 44, 88)
EDGE = (96, 120, 210)
TEXT = (236, 240, 255)
TEXT_DIM = (156, 168, 214)
ACCENT = (110, 220, 255)
GOLD = (255, 204, 84)
GREEN = (90, 240, 150)
RED = (255, 92, 92)
ORANGE = (255, 160, 60)
PINK = (255, 110, 200)
STEEL = (180, 188, 204)
BRASS = (214, 172, 84)
FUSE = (150, 104, 56)
FUSE_DARK = (82, 54, 26)
EMBER = (255, 170, 60)

_fonts = {}
_cache = {}


def font(size, kind="bold"):
    key = (size, kind)
    if key not in _fonts:
        name = {"bold": "MPLUS1p-Bold.ttf", "regular": "MPLUS1p-Regular.ttf", "display": "Orbitron.ttf"}[kind]
        try:
            f = pygame.font.Font(asset("fonts", name), size)
            if kind == "display":
                f.set_bold(True)
        except (OSError, pygame.error):
            f = pygame.font.Font(None, size)
        _fonts[key] = f
    return _fonts[key]


def render(text, size, color=TEXT, kind="bold"):
    key = ("txt", text, size, color, kind)
    surf = _cache.get(key)
    if surf is None:
        surf = font(size, kind).render(text, True, color)
        if len(_cache) > 6000:
            for k in [k for k in _cache if k[0] == "txt"]:
                del _cache[k]
        _cache[key] = surf
    return surf


def text(surface, s, pos, size=20, color=TEXT, kind="bold", anchor="topleft", shadow=False, alpha=255):
    img = render(s, size, color, kind)
    rect = img.get_rect(**{anchor: (int(pos[0]), int(pos[1]))})
    if shadow:
        sh = render(s, size, (0, 0, 0), kind)
        sh = sh.copy()
        sh.set_alpha(140 * alpha // 255)
        surface.blit(sh, rect.move(2, 2))
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surface.blit(img, rect)
    return rect


CLOSING = set("、。，．）」』！？：・ー")


def _is_cjk(ch):
    return ord(ch) > 0x2E7F


def wrap(s, size, width, kind="bold"):
    """Wrap English at spaces and Japanese between characters."""
    f = font(size, kind)
    lines = []
    for para in s.split("\n"):
        tokens = []
        word = ""
        for ch in para:
            if _is_cjk(ch):
                if word:
                    tokens.append(word)
                    word = ""
                tokens.append(ch)
            elif ch == " ":
                word += ch
                tokens.append(word)
                word = ""
            else:
                word += ch
        if word:
            tokens.append(word)
        line = ""
        for tok in tokens:
            trial = line + tok
            if f.size(trial.rstrip())[0] <= width or not line or tok in CLOSING:
                line = trial
            else:
                lines.append(line.rstrip())
                # keep Japanese closing punctuation on the previous line
                line = tok.lstrip()
        lines.append(line.rstrip())
    return lines


def paragraph(surface, s, rect, size=18, color=TEXT, kind="bold", spacing=1.3, align="left"):
    rect = pygame.Rect(rect)
    y = rect.top
    for line in wrap(s, size, rect.width, kind):
        if align == "center":
            text(surface, line, (rect.centerx, y), size, color, kind, anchor="midtop")
        else:
            text(surface, line, (rect.left, y), size, color, kind)
        y += int(size * spacing)
    return y


def gradient(size, top, bottom, horizontal=False):
    w, h = size
    surf = pygame.Surface((w, h))
    steps = w if horizontal else h
    for i in range(steps):
        t = i / max(1, steps - 1)
        c = [int(top[k] + (bottom[k] - top[k]) * t) for k in range(3)]
        if horizontal:
            pygame.draw.line(surf, c, (i, 0), (i, h))
        else:
            pygame.draw.line(surf, c, (0, i), (w, i))
    return surf


def glow(radius, color, strength=1.0):
    """Soft radial light, premultiplied, for additive blending."""
    key = ("glow", radius, color, round(strength, 2))
    if key in _cache:
        return _cache[key]
    surf = pygame.Surface((radius * 2, radius * 2))
    surf.fill((0, 0, 0))
    for r in range(radius, 0, -1):
        t = r / radius
        k = strength * (1 - t) ** 2.2
        pygame.draw.circle(surf, tuple(min(255, int(c * k)) for c in color), (radius, radius), r)
    _cache[key] = surf
    return surf


def blit_glow(surface, center, radius, color, strength=1.0):
    g = glow(max(2, int(radius)), color, strength)
    surface.blit(g, g.get_rect(center=(int(center[0]), int(center[1]))), special_flags=pygame.BLEND_RGB_ADD)


def panel(surface, rect, color=PANEL, border=EDGE, radius=16, alpha=235, shadow=True, width=2):
    rect = pygame.Rect(rect)
    key = ("panel", rect.size, color, radius, alpha, shadow)
    cached = _cache.get(key)
    if cached is None:
        sh = None
        if shadow:
            sh = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
            for i in range(8, 0, -2):
                pygame.draw.rect(sh, (0, 0, 0, 18), sh.get_rect().inflate(-i * 2 + 4, -i * 2 + 4).move(0, 2),
                                 border_radius=radius + i)
        body = pygame.Surface(rect.size, pygame.SRCALPHA)
        top = tuple(min(255, c + 12) for c in color)
        for y in range(rect.h):
            t = y / max(1, rect.h - 1)
            c = [int(top[k] + (color[k] - top[k]) * t) for k in range(3)]
            pygame.draw.line(body, (*c, alpha), (0, y), (rect.w, y))
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        cached = (sh, body)
        _cache[key] = cached
    sh, body = cached
    if sh is not None:
        surface.blit(sh, (rect.x - 8, rect.y - 4))
    surface.blit(body, rect)
    if border:
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)
        hl = pygame.Rect(rect.x + radius, rect.y + 1, rect.w - radius * 2, 1)
        pygame.draw.rect(surface, tuple(min(255, c + 60) for c in border), hl)


def aaline(surface, color, p1, p2, width=2):
    """Thick anti-aliased line with round caps."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 0.01:
        pygame.gfxdraw.filled_circle(surface, int(x1), int(y1), max(1, int(width / 2)), color)
        return
    if width <= 1.5:
        pygame.draw.aaline(surface, color, p1, p2)
        return
    nx, ny = -dy / length * width / 2, dx / length * width / 2
    pts = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
    pygame.gfxdraw.aapolygon(surface, pts, color)
    pygame.gfxdraw.filled_polygon(surface, pts, color)
    r = int(width / 2)
    for x, y in (p1, p2):
        pygame.gfxdraw.aacircle(surface, int(x), int(y), r, color)
        pygame.gfxdraw.filled_circle(surface, int(x), int(y), r, color)


def circle(surface, color, center, radius, width=0):
    x, y, r = int(center[0]), int(center[1]), int(radius)
    if r < 1:
        return
    if width == 0:
        pygame.gfxdraw.aacircle(surface, x, y, r, color)
        pygame.gfxdraw.filled_circle(surface, x, y, r, color)
    else:
        for i in range(width):
            pygame.gfxdraw.aacircle(surface, x, y, r - i, color)


def shade(color, amount):
    return tuple(max(0, min(255, int(c + amount))) for c in color)


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))



def gradient_text(s, size, top, bottom, kind="display", outline=None):
    """Text filled with a vertical gradient, with an optional dark outline."""
    key = ("gtext", s, size, top, bottom, kind, outline)
    if key in _cache:
        return _cache[key]
    s2 = s
    mask = font(size, kind).render(s2, True, (255, 255, 255))
    w, h = mask.get_size()
    pad = 4 if outline else 0
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    if outline:
        dark = font(size, kind).render(s2, True, outline)
        for dx in range(-pad, pad + 1, 2):
            for dy in range(-pad, pad + 1, 2):
                out.blit(dark, (pad + dx, pad + dy))
    fill = gradient((w, h), top, bottom).convert_alpha()
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    out.blit(fill, (pad, pad))
    _cache[key] = out
    return out


# ---------------------------------------------------------------- night sky

class Sky:
    """Night sky with twinkling stars and a city skyline along the bottom."""

    def __init__(self, size, seed=3, skyline=True):
        self.size = size
        rng = random.Random(seed)
        w, h = size
        base = gradient(size, BG_TOP, BG_BOTTOM)
        # soft nebula clouds
        haze = pygame.Surface(size)
        haze.fill((0, 0, 0))
        for _ in range(9):
            col = rng.choice([(40, 20, 70), (20, 30, 80), (60, 20, 60), (16, 40, 70)])
            r = rng.randint(140, 320)
            g = glow(r, col, 0.55)
            haze.blit(g, (rng.randint(-r, w - r), rng.randint(-r, int(h * 0.7) - r)),
                      special_flags=pygame.BLEND_RGB_ADD)
        base.blit(haze, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        for _ in range(420):
            x, y = rng.randrange(w), rng.randrange(int(h * 0.85))
            v = rng.randint(50, 140)
            base.set_at((x, y), (v, v, min(255, v + 30)))
        self.stars = [(rng.randrange(w), rng.randrange(int(h * 0.75)), rng.uniform(0, 6.28),
                       rng.uniform(0.6, 2.2), rng.choice([(255, 255, 255), (190, 210, 255), (255, 230, 200)]))
                      for _ in range(70)]
        self.ground = h
        if skyline:
            self._skyline(base, rng)
        self.base = base.convert() if pygame.display.get_init() and pygame.display.get_surface() else base

    def _skyline(self, base, rng):
        w, h = self.size
        far = pygame.Surface((w, h), pygame.SRCALPHA)
        x = -10
        while x < w:
            bw, bh = rng.randint(30, 80), rng.randint(30, 90)
            pygame.draw.rect(far, (24, 18, 52, 255), (x, h - 30 - bh, bw, bh + 30))
            x += bw + rng.randint(-6, 4)
        base.blit(far, (0, 0))
        x = -10
        while x < w:
            bw, bh = rng.randint(40, 110), rng.randint(40, 130)
            top = h - 26 - bh
            col = (12, 10, 30)
            pygame.draw.rect(base, col, (x, top, bw, bh + 26))
            if rng.random() < 0.3:
                pygame.draw.rect(base, col, (x + bw // 3, top - 14, bw // 3, 14))
                if rng.random() < 0.5:
                    pygame.draw.line(base, col, (x + bw // 2, top - 14), (x + bw // 2, top - 34), 2)
            for wx in range(x + 6, x + bw - 8, 11):
                for wy in range(top + 8, h - 34, 14):
                    if rng.random() < 0.22:
                        c = rng.choice([(255, 210, 120), (255, 190, 90), (180, 210, 255)])
                        k = rng.uniform(0.35, 0.8)
                        pygame.draw.rect(base, tuple(int(v * k) for v in c), (wx, wy, 5, 7))
            x += bw + rng.randint(0, 10)
        pygame.draw.rect(base, (8, 6, 20), (0, h - 26, w, 26))
        pygame.draw.line(base, (40, 34, 80), (0, h - 26), (w, h - 26), 1)
        self.ground = h - 26

    def draw(self, surface, t):
        surface.blit(self.base, (0, 0))
        for x, y, ph, sp, col in self.stars:
            k = 0.5 + 0.5 * math.sin(t * sp + ph)
            if k > 0.25:
                blit_glow(surface, (x, y), 5, col, 0.45 * k)
                surface.set_at((x, y), col)


# ---------------------------------------------------------------- toggle switch

def _metal_plate(size, radius, base=(84, 90, 108)):
    key = ("plate", size, radius, base)
    if key in _cache:
        return _cache[key]
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body = gradient(size, shade(base, 45), shade(base, -40)).convert_alpha()
    rng = random.Random(w * 31 + h)
    for y in range(0, h, 3):  # faint brushed metal
        v = rng.randint(-8, 8)
        pygame.draw.line(body, (*shade(base, v + 10), 28), (0, y), (w, y))
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (0, 0))
    pygame.draw.rect(surf, shade(base, 90), surf.get_rect(), 2, border_radius=radius)
    pygame.draw.rect(surf, shade(base, -50), surf.get_rect().inflate(-4, -4), 1, border_radius=radius - 2)
    r = max(2, w // 18)
    for cx in (r + 5, w - r - 6):
        for cy in (r + 5, h - r - 6):
            circle(surf, shade(base, -45), (cx, cy + 1), r + 1)
            circle(surf, shade(base, 60), (cx, cy), r)
            pygame.draw.line(surf, shade(base, -40), (cx - r + 1, cy - r + 2), (cx + r - 2, cy + r - 1), 1)
    _cache[key] = surf
    return surf


def switch_layout(rect):
    """Where each piece of a switch sits inside its slot."""
    r = pygame.Rect(rect)
    w = r.w
    plate_w = int(min(w * 0.8, max(74, r.h * 0.36)))
    plate_h = int(r.h * 0.54)
    return {
        "value": pygame.Rect(r.centerx - plate_w // 2, r.y, plate_w, int(r.h * 0.13)),
        "led": (r.centerx, r.y + int(r.h * 0.2)),
        "plate": pygame.Rect(r.centerx - plate_w // 2, r.y + int(r.h * 0.26), plate_w, plate_h),
        "digit": (r.centerx, r.y + int(r.h * 0.89)),
        "fuse_y": r.bottom + 10,
    }


def draw_switch(surface, rect, pos, value_text=None, selected=False, hover=0.0, flash=0.0, scale=1.0):
    """A metal toggle switch. pos: 0 = OFF (lever down) .. 1 = ON (lever up)."""
    lay = switch_layout(rect)
    r = pygame.Rect(rect)
    on = pos > 0.5
    if selected:
        sel = r.inflate(10, 10)
        pygame.draw.rect(surface, ACCENT, sel, 2, border_radius=14)
    if hover > 0.02:
        blit_glow(surface, lay["plate"].center, int(r.w * 0.8), (60, 90, 160), 0.35 * hover)
    # place value plate
    if value_text is not None:
        vr = lay["value"]
        pygame.draw.rect(surface, (14, 18, 44), vr, border_radius=8)
        pygame.draw.rect(surface, shade(GOLD, -60) if on else (70, 80, 130), vr, 2, border_radius=8)
        size = int(vr.h * (0.62 if len(value_text) < 4 else 0.5 if len(value_text) < 5 else 0.42))
        text(surface, value_text, vr.center, max(10, int(size * 1.15)), GOLD if on else TEXT_DIM, "bold",
             anchor="center")
    # LED
    lx, ly = lay["led"]
    lr = max(5, int(r.w * 0.1))
    circle(surface, (20, 20, 30), (lx, ly), lr + 3)
    if on:
        blit_glow(surface, (lx, ly), lr * 5, (60, 255, 140), 0.7 + 0.3 * flash)
        circle(surface, (120, 255, 170), (lx, ly), lr)
        circle(surface, (230, 255, 240), (lx - lr // 3, ly - lr // 3), max(1, lr // 3))
    else:
        circle(surface, (60, 20, 26), (lx, ly), lr)
        circle(surface, (110, 50, 60), (lx - lr // 3, ly - lr // 3), max(1, lr // 4))
    # plate and labels
    pr = lay["plate"]
    surface.blit(_metal_plate(pr.size, 10), pr)
    small = max(8, pr.w // 7)
    text(surface, "ON", (pr.centerx, pr.y + pr.h * 0.1), small, (110, 255, 160) if on else (120, 128, 150),
         "display", anchor="center")
    text(surface, "OFF", (pr.centerx, pr.bottom - pr.h * 0.1), small, (120, 128, 150) if on else (255, 120, 120),
         "display", anchor="center")
    # lever: a chrome bat with an orange cap, pointing up for ON and down for OFF
    cx, cy = pr.center
    nut = max(8, int(pr.w * 0.2))
    circle(surface, (30, 32, 42), (cx + 2, cy + 3), nut + 5)
    for i in range(nut + 4, 0, -1):
        k = i / (nut + 4)
        circle(surface, shade((150, 156, 172), 80 - 150 * k), (cx - (1 - k) * 2, cy - (1 - k) * 2), i)
    circle(surface, (36, 40, 52), (cx, cy), int(nut * 0.6))
    d = max(-1.0, min(1.0, pos * 2 - 1))
    length = pr.h * 0.25
    tip = (cx, cy - length * d)
    base_w, tip_w = nut * 0.5, nut * 0.36
    if abs(d) > 0.08:
        off = 5 * abs(d)
        shadow = [(cx - base_w + off, cy + off), (cx + base_w + off, cy + off),
                  (tip[0] + tip_w + off, tip[1] + off), (tip[0] - tip_w + off, tip[1] + off)]
        pygame.gfxdraw.filled_polygon(surface, shadow, (36, 38, 50))
        for frac, col in ((1.0, (120, 126, 142)), (0.62, (200, 206, 220)), (0.22, (250, 252, 255))):
            shaft = [(cx - base_w * frac - (1 - frac) * base_w * 0.4, cy), (cx + base_w * frac - (1 - frac) * base_w * 0.4, cy),
                     (tip[0] + tip_w * frac - (1 - frac) * tip_w * 0.4, tip[1]),
                     (tip[0] - tip_w * frac - (1 - frac) * tip_w * 0.4, tip[1])]
            pygame.gfxdraw.aapolygon(surface, shaft, col)
            pygame.gfxdraw.filled_polygon(surface, shaft, col)
    cap = nut * 0.55 + (1 - abs(d)) * nut * 0.25
    cap_col = (255, 140, 40) if on else (220, 90, 50)
    circle(surface, (40, 20, 10), (tip[0] + 2, tip[1] + 3), cap + 1)
    circle(surface, shade(cap_col, -70), tip, cap + 1)
    circle(surface, cap_col, (tip[0] - 1, tip[1] - 1), cap)
    circle(surface, shade(cap_col, 80), (tip[0] - cap * 0.35, tip[1] - cap * 0.35), max(1, cap * 0.38))
    # big bit digit
    digit = "1" if on else "0"
    dsize = int(min(r.w * 0.55, r.h * 0.15))
    if on:
        blit_glow(surface, lay["digit"], dsize, (255, 180, 60), 0.5 + 0.5 * flash)
    text(surface, digit, lay["digit"], dsize, GOLD if on else (90, 100, 140), "bold", anchor="center")
    if flash > 0.01:
        blit_glow(surface, pr.center, int(r.w * 1.1), (255, 200, 120), 0.6 * flash)


# ---------------------------------------------------------------- mortar tubes

def mortar(height, width, color):
    key = ("mortar", height, width, color)
    if key in _cache:
        return _cache[key]
    w, h = width, height
    surf = pygame.Surface((w + 8, h + 12), pygame.SRCALPHA)
    body = gradient((w, h), shade(color, -60), shade(color, -60), horizontal=True).convert_alpha()
    for x in range(w):
        k = math.sin(math.pi * x / w)
        light = int(-70 + 110 * k ** 0.8 - (25 if x > w * 0.6 else 0))
        pygame.draw.line(body, (*shade(color, light), 255), (x, 0), (x, h))
    for by in (int(h * 0.25), int(h * 0.7)):
        pygame.draw.rect(body, (*shade(GOLD, -40), 255), (0, by, w, max(2, h // 12)))
    surf.blit(body, (4, 6))
    pygame.draw.ellipse(surf, shade(color, 40), (4, 0, w, 12))
    pygame.draw.ellipse(surf, (16, 10, 12), (7, 2, w - 6, 8))
    pygame.draw.ellipse(surf, (0, 0, 0, 120), (0, h + 2, w + 8, 10))
    _cache[key] = surf
    return surf


def draw_mortar(surface, center_bottom, height, width, color, flash=0.0):
    img = mortar(int(height), int(width), color)
    rect = img.get_rect(midbottom=(int(center_bottom[0]), int(center_bottom[1])))
    surface.blit(img, rect)
    if flash > 0.01:
        blit_glow(surface, (rect.centerx, rect.y + 6), int(width * 2.2), (255, 190, 90), flash)
    return (rect.centerx, rect.y + 6)
