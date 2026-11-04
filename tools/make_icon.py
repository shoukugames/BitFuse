#!/usr/bin/env python3
"""Draw the game icon with the game's own art: assets/icon.png and assets/icon.ico.

Run this only when the design changes. Needs Pillow for the .ico file.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)

import pygame  # noqa: E402
from PIL import Image  # noqa: E402

from bitfuse import art  # noqa: E402

pygame.init()
pygame.display.set_mode((16, 16))
SIZE = 512
canvas = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
back = art.gradient((SIZE, SIZE), (12, 14, 48), (60, 26, 90)).convert_alpha()
glowlayer = pygame.Surface((SIZE, SIZE))
glowlayer.fill((0, 0, 0))
# a firework burst behind the switch
import math  # noqa: E402
for i in range(36):
    a = i / 36 * math.tau
    for k in range(5):
        r = 90 + k * 34
        x, y = 330 + math.cos(a) * r, 150 + math.sin(a) * r * 0.9
        col = (255, 120 + k * 25, 60 + k * 30) if i % 2 else (90, 220, 255)
        art.blit_glow(glowlayer, (x, y), 12 - k, col, 1.0 - k * 0.15)
back.blit(glowlayer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
mask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=110)
back.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
canvas.blit(back, (0, 0))
art.draw_switch(canvas, pygame.Rect(156, 50, 200, 400), 1.0, None)
# the fuse with a spark
pygame.draw.line(canvas, art.FUSE_DARK, (40, 452), (472, 452), 22)
pygame.draw.line(canvas, art.FUSE, (40, 452), (472, 452), 14)
for x in range(40, 330, 14):
    pygame.draw.line(canvas, (205, 160, 100), (x - 5, 446), (x + 5, 458), 3)
pygame.draw.line(canvas, (40, 36, 40), (330, 452), (472, 452), 16)
spark = pygame.Surface((SIZE, SIZE))
spark.fill((0, 0, 0))
art.blit_glow(spark, (330, 452), 90, (255, 150, 40), 1.0)
art.blit_glow(spark, (330, 452), 26, (255, 255, 230), 1.0)
canvas.blit(spark, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
canvas.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
out = os.path.join(ROOT, "assets", "icon.png")
pygame.image.save(canvas, out)
Image.open(out).save(os.path.join(ROOT, "assets", "icon.ico"),
                     sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icon written")
