"""The fuse: one braided cord that runs through every switch and on to the mortars."""
import math

import pygame

from . import art


class Fuse:
    def __init__(self, points, size):
        self.points = [(float(x), float(y)) for x, y in points]
        self.dist = [0.0]
        for p, q in zip(self.points, self.points[1:]):
            self.dist.append(self.dist[-1] + math.dist(p, q))
        self.length = self.dist[-1]
        self.size = size
        self._image = None

    def at(self, d):
        """Point and direction at distance d along the fuse."""
        d = max(0.0, min(self.length, d))
        for i in range(1, len(self.dist)):
            if self.dist[i] >= d:
                p, q = self.points[i - 1], self.points[i]
                seg = self.dist[i] - self.dist[i - 1] or 1.0
                k = (d - self.dist[i - 1]) / seg
                return (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k), ((q[0] - p[0]) / seg, (q[1] - p[1]) / seg)
        return self.points[-1], (1.0, 0.0)

    def distance_to_x(self, x, y_hint=None):
        """Distance along the fuse where it first passes x (on the segment nearest y_hint)."""
        best = None
        for i in range(1, len(self.points)):
            (x1, y1), (x2, y2) = self.points[i - 1], self.points[i]
            if min(x1, x2) - 0.5 <= x <= max(x1, x2) + 0.5 and abs(x2 - x1) > 0.5:
                k = (x - x1) / (x2 - x1)
                y = y1 + (y2 - y1) * k
                d = self.dist[i - 1] + (self.dist[i] - self.dist[i - 1]) * k
                score = abs(y - y_hint) if y_hint is not None else 0
                if best is None or score < best[0]:
                    best = (score, d)
        return best[1] if best else 0.0

    def _render(self):
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pts = self.points
        for p, q in zip(pts, pts[1:]):
            art.aaline(surf, (30, 18, 8), (p[0] + 2, p[1] + 3), (q[0] + 2, q[1] + 3), 8)
        for p, q in zip(pts, pts[1:]):
            art.aaline(surf, art.FUSE_DARK, p, q, 8)
        for p, q in zip(pts, pts[1:]):
            art.aaline(surf, art.FUSE, p, q, 5)
        # braid: little diagonal twists every few pixels
        d = 0.0
        while d < self.length:
            (x, y), (dx, dy) = self.at(d)
            nx, ny = -dy, dx
            a = (x + nx * 3 - dx * 2, y + ny * 3 - dy * 2)
            b = (x - nx * 3 + dx * 2, y - ny * 3 + dy * 2)
            pygame.draw.aaline(surf, (205, 160, 100), a, b)
            d += 6
        self._image = surf

    def draw(self, surface, burnt=0.0, t=0.0):
        if self._image is None:
            self._render()
        surface.blit(self._image, (0, 0))
        if burnt <= 0:
            return
        burnt = min(burnt, self.length)
        # ash where the fuse has burnt, with embers just behind the spark
        prev = self.points[0]
        for i in range(1, len(self.points)):
            if self.dist[i - 1] >= burnt:
                break
            end = self.points[i] if self.dist[i] <= burnt else self.at(burnt)[0]
            art.aaline(surface, (24, 20, 22), prev, end, 6)
            art.aaline(surface, (64, 58, 60), prev, end, 2)
            prev = self.points[i]
        d = max(0.0, burnt - 70)
        while d < burnt:
            (x, y), _ = self.at(d)
            k = 1 - (burnt - d) / 70
            flicker = 0.6 + 0.4 * math.sin(t * 40 + d)
            art.blit_glow(surface, (x, y), 4 + int(6 * k), art.EMBER, round(0.9 * k * flicker, 1))
            d += 7
