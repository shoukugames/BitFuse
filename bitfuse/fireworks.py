"""Fireworks: rockets that climb from the mortars and burst into many patterns.

Particles are drawn as soft glows onto a light layer that fades a little every
frame, so every spark leaves a glowing trail. The layer is added onto the
screen, which makes overlapping sparks brighten like real light.
"""
import math
import random

import pygame

from . import art

COLORS = {
    "red": (255, 70, 70), "orange": (255, 150, 40), "gold": (255, 200, 90), "yellow": (255, 240, 110),
    "green": (90, 255, 120), "cyan": (80, 230, 255), "blue": (90, 130, 255), "purple": (190, 100, 255),
    "pink": (255, 110, 210), "white": (240, 240, 255), "silver": (200, 210, 230),
}
PALETTES = [("red", "gold"), ("cyan", "white"), ("green", "yellow"), ("purple", "pink"), ("blue", "silver"),
            ("orange", "gold"), ("pink", "white"), ("gold", "red"), ("green", "cyan"), ("purple", "gold")]
MAX_PARTICLES = 2800
LEVELS = 8  # brightness steps for the glow sprites
ADD = pygame.BLEND_RGB_ADD
FLASH_RADII = (140, 200, 260)
FLASH_COLOR = (255, 226, 190)


def prewarm():
    """Draw the big burst-flash glows once, so the first bursts never stutter."""
    for r in FLASH_RADII:
        for k in range(1, 5):
            art.glow(r, FLASH_COLOR, 0.09 * k)


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max", "color", "size", "drag", "grav", "kind", "data")

    def __init__(self, x, y, vx, vy, life, color, size=3.0, drag=1.4, grav=60.0, kind=0, data=None):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max = life
        self.color, self.size, self.drag, self.grav, self.kind, self.data = color, size, drag, grav, kind, data


# particle kinds
PLAIN, TRAIL, STROBE, SPLIT, GLITTER, ROCKET = range(6)


class Fireworks:
    def __init__(self, size, sound=None, seed=None):
        self.size = size
        self.layer = pygame.Surface(size)
        self.layer.fill((0, 0, 0))
        self.parts = []
        self.sound = sound or (lambda *a, **k: None)
        self.rng = random.Random(seed)
        self.sprites = {}
        self.t = 0.0
        self.flashes = []

    def clear(self):
        self.parts.clear()
        self.layer.fill((0, 0, 0))

    @property
    def busy(self):
        return bool(self.parts)

    # ------------------------------------------------------------ launching
    def launch(self, x, y, kind="peony", scale=1.0, palette=None, apex=None):
        rng = self.rng
        palette = palette or rng.choice(PALETTES)
        h = self.size[1]
        apex = apex if apex is not None else rng.uniform(h * 0.12, h * 0.42)
        # speed needed to reach the apex against the rocket's gravity
        g = 260.0
        vy = -math.sqrt(max(1.0, 2 * g * max(40.0, y - apex)))
        rocket = Particle(x, y, rng.uniform(-18, 18), vy, 6.0, COLORS["gold"], 3.2, 0.0, g, ROCKET,
                          (kind, scale, palette))
        self.parts.append(rocket)
        self.sound("launch", self._pan(x))

    def _pan(self, x):
        return max(-1.0, min(1.0, x / self.size[0] * 2 - 1))

    def burst(self, x, y, kind, scale, palette):
        rng = self.rng
        c1, c2 = COLORS[palette[0]], COLORS[palette[1]]
        add = self.parts.append
        room = MAX_PARTICLES - len(self.parts)
        if room < 40:
            return
        speed = 210 * scale
        n = int(min(room, 90 * scale))
        self.flashes.append([x, y, 0.35, 120 + 90 * scale, c1])
        self.sound("boom_big" if scale > 1.2 else "boom", self._pan(x))

        def sphere(count, spd, color, life=1.7, size=3.2, kind_=PLAIN, drag=1.5, grav=55):
            for i in range(count):
                a = rng.uniform(0, math.tau)
                # uniform on a sphere, seen from the side
                z = rng.uniform(-1, 1)
                k = math.sqrt(1 - z * z) * spd * rng.uniform(0.92, 1.05)
                add(Particle(x, y, math.cos(a) * k, math.sin(a) * k, life * rng.uniform(0.8, 1.15), color,
                             size, drag, grav, kind_))

        if kind == "peony":
            sphere(n, speed, c1)
            sphere(n // 4, speed * 0.45, c2, 1.3, 2.6)
        elif kind == "ring":
            tilt = rng.uniform(0.35, 1.0)
            spin = rng.uniform(0, math.pi)
            m = int(n * 0.8)
            for i in range(m):
                a = i / m * math.tau
                vx, vy = math.cos(a) * speed, math.sin(a) * speed * tilt
                vx, vy = vx * math.cos(spin) - vy * math.sin(spin), vx * math.sin(spin) + vy * math.cos(spin)
                add(Particle(x, y, vx, vy, 1.6, c1 if i % 2 else c2, 3.4, 1.3, 40))
            sphere(n // 5, speed * 0.25, COLORS["white"], 1.0, 2.4)
        elif kind == "willow":
            sphere(int(n * 0.9), speed * 0.8, COLORS["gold"], 3.2, 2.6, TRAIL, 2.2, 75)
        elif kind == "crossette":
            for i in range(14):
                a = i / 14 * math.tau + rng.uniform(-0.1, 0.1)
                add(Particle(x, y, math.cos(a) * speed * 0.75, math.sin(a) * speed * 0.75, 0.75, c1, 4.2,
                             1.0, 50, SPLIT, (c2, scale)))
        elif kind == "palm":
            arms = 8
            for i in range(arms):
                a = i / arms * math.tau + rng.uniform(-0.15, 0.15) - math.pi / 2
                for j in range(9):
                    k = speed * (0.55 + j * 0.06)
                    add(Particle(x, y, math.cos(a) * k, math.sin(a) * k - 40, 2.3, COLORS["gold"], 4.0 - j * 0.2,
                                 1.7, 85, TRAIL))
            sphere(n // 4, speed * 0.3, c1, 1.2, 2.8)
        elif kind == "glitter":
            sphere(n, speed * 0.9, COLORS["silver"], 2.2, 2.4, GLITTER, 1.8, 60)
            self.sound("crackle", self._pan(x))
        elif kind == "double":
            sphere(int(n * 0.7), speed, c1)
            sphere(int(n * 0.5), speed * 0.55, c2, 1.7, 3.0)
        elif kind == "strobe":
            sphere(n, speed * 0.85, COLORS["white"], 2.4, 3.0, STROBE, 1.6, 50)
            self.sound("crackle", self._pan(x))
        elif kind == "heart":
            m = int(n * 0.9)
            for i in range(m):
                a = i / m * math.tau
                hx = 16 * math.sin(a) ** 3
                hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
                k = speed / 16
                add(Particle(x, y, hx * k, hy * k, 1.8, COLORS["pink"] if i % 3 else COLORS["red"], 3.4, 1.2, 25))
        elif kind == "galaxy":
            sphere(int(n * 0.6), speed * 0.7, c1, 1.9)
            tilt = 0.3
            m = int(n * 0.7)
            for i in range(m):
                a = i / m * math.tau
                add(Particle(x, y, math.cos(a) * speed * 1.25, math.sin(a) * speed * 1.25 * tilt, 2.0, c2, 3.0,
                             1.3, 20))
        else:
            sphere(n, speed, c1)

    # ------------------------------------------------------------ simulation
    def update(self, dt):
        self.t += dt
        rng = self.rng
        alive = []
        add = alive.append
        new = []
        for p in self.parts:
            p.life -= dt
            if p.kind == ROCKET:
                p.vy += p.grav * dt
                p.x += p.vx * dt
                p.y += p.vy * dt
                if rng.random() < 0.9:
                    new.append(Particle(p.x + rng.uniform(-2, 2), p.y + 4, rng.uniform(-25, 25),
                                        rng.uniform(20, 80), rng.uniform(0.3, 0.6), COLORS["orange"], 2.2, 2.5, 40))
                if p.vy >= -30 or p.life <= 0:
                    kind, scale, palette = p.data
                    self.burst(p.x, p.y, kind, scale, palette)
                    continue
                add(p)
                continue
            if p.life <= 0:
                if p.kind == SPLIT:
                    color, scale = p.data
                    for i in range(4):
                        a = i / 4 * math.tau + math.pi / 4
                        new.append(Particle(p.x, p.y, p.vx * 0.3 + math.cos(a) * 110 * scale,
                                            p.vy * 0.3 + math.sin(a) * 110 * scale, 1.0, color, 3.0, 1.6, 60))
                    if rng.random() < 0.3:
                        self.sound("crackle", self._pan(p.x))
                continue
            drag = math.exp(-p.drag * dt)
            p.vx *= drag
            p.vy = p.vy * drag + p.grav * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            if p.kind == TRAIL and rng.random() < 0.22:
                new.append(Particle(p.x, p.y, 0, 15, 0.5, p.color, 1.8, 3.0, 30))
            add(p)
        alive.extend(new[: max(0, MAX_PARTICLES - len(alive))])
        self.parts = alive
        for f in self.flashes:
            f[2] -= dt
        self.flashes = [f for f in self.flashes if f[2] > 0]

    def _sprite(self, color, radius, level):
        key = (color, radius, level)
        s = self.sprites.get(key)
        if s is None:
            k = (level + 1) / LEVELS
            s = art.glow(radius, tuple(int(c * k) for c in color), 1.0)
            self.sprites[key] = s
        return s

    def draw(self, surface, fade=200):
        layer = self.layer
        # a multiply-blit of a grey sheet is many times faster than a multiply-fill
        dim = self.sprites.get(("fade", fade))
        if dim is None:
            dim = self.sprites[("fade", fade)] = pygame.Surface(self.size)
            dim.fill((fade, fade, fade))
        layer.blit(dim, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        blits = []
        add = blits.append
        sprites = self.sprites
        t14 = self.t * 14
        rand = self.rng.random
        top = LEVELS - 1
        for p in self.parts:
            kind = p.kind
            if kind == ROCKET:
                k = 1.0
            else:
                k = p.life / p.max
                if k <= 0:
                    continue
                if kind == STROBE and int(t14 + p.x) % 3 == 0:
                    continue
                if kind == GLITTER and rand() < 0.45:
                    continue
                k = k ** 0.7
            level = int(k * LEVELS)
            if level > top:
                level = top
            radius = int(p.size * (1.2 + 1.6 * k))
            if radius < 2:
                radius = 2
            key = (p.color, radius, level)
            spr = sprites.get(key)
            if spr is None:
                spr = self._sprite(p.color, radius, level)
            x, y = int(p.x), int(p.y)
            add((spr, (x - radius, y - radius), None, ADD))
            if k > 0.7 and kind != TRAIL:
                core = sprites.get(("core", level))
                if core is None:
                    core = sprites[("core", level)] = self._sprite((255, 255, 255), 2, level)
                add((core, (x - 2, y - 2), None, ADD))
        if blits:
            layer.blits(blits, doreturn=False)
        surface.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        for x, y, life, radius, _color in self.flashes:
            r = FLASH_RADII[min(len(FLASH_RADII) - 1, int(radius) // 100)]
            k = max(1, min(4, int(life / 0.35 * 4 + 0.5)))
            art.blit_glow(surface, (x, y), r, FLASH_COLOR, 0.09 * k)
