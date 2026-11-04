"""The 100 levels: how many switches, which number, and how big the fireworks are.

Levels are generated from the level number, the difficulty and a random
source, so every game is different but always follows the same curve:
more switches and larger numbers as the levels go up.
"""
import random
from dataclasses import dataclass, field

LEVELS = 100
TIME_LIMIT = 99
POINTS_PER_SECOND = 100
DIFFICULTIES = ("easy", "medium", "hard")

RULES = {
    # min/max switches, seconds lost on a wrong answer, from which level switches
    # start in a random position, until which level place values are printed,
    # whether the running total is shown
    "easy": {"min_bits": 3, "max_bits": 8, "penalty": 3, "scramble_from": None,
             "values_until": LEVELS, "total": True},
    "medium": {"min_bits": 4, "max_bits": 12, "penalty": 5, "scramble_from": 41,
               "values_until": LEVELS, "total": False},
    "hard": {"min_bits": 5, "max_bits": 16, "penalty": 8, "scramble_from": 1,
             "values_until": 20, "total": False},
}

SHELL_UNLOCKS = [(1, "peony"), (4, "ring"), (10, "willow"), (18, "crossette"), (26, "palm"),
                 (34, "glitter"), (45, "double"), (55, "strobe"), (70, "heart"), (85, "galaxy")]


@dataclass
class Level:
    number: int
    difficulty: str
    bits: int
    target: int
    start: list = field(default_factory=list)   # starting switch states, most significant first
    show_values: bool = True
    show_total: bool = False
    penalty: int = 3

    @property
    def answer(self):
        return to_bits(self.target, self.bits)


def to_bits(value, bits):
    """Most significant first: to_bits(5, 4) == [0, 1, 0, 1]"""
    return [(value >> (bits - 1 - i)) & 1 for i in range(bits)]


def from_bits(states):
    value = 0
    for s in states:
        value = value * 2 + (1 if s else 0)
    return value


def bits_for(number, difficulty):
    r = RULES[difficulty]
    span = r["max_bits"] - r["min_bits"] + 1
    return min(r["max_bits"], r["min_bits"] + (number - 1) * span // LEVELS)


def generate(number, difficulty, rng=None, previous=None):
    rng = rng or random.Random()
    number = max(1, min(LEVELS, number))
    r = RULES[difficulty]
    bits = bits_for(number, difficulty)
    top = (1 << bits) - 1
    # Within a band of levels with the same switch count the numbers climb from
    # the lower half of the range into the top half.
    band_start = next(n for n in range(1, number + 1) if bits_for(n, difficulty) == bits)
    band_end = max(n for n in range(number, LEVELS + 1) if bits_for(n, difficulty) == bits)
    progress = (number - band_start) / max(1, band_end - band_start)
    half = 1 << (bits - 1)
    if number <= 2:
        low, high = 1, top
    else:
        low = int(half * (0.55 + 0.45 * progress)) if bits > 3 else half
        low = max(2, low)
        high = top
    target = rng.randint(low, high)
    for _ in range(8):
        if target != previous:
            break
        target = rng.randint(low, high)
    start = [0] * bits
    if r["scramble_from"] is not None and number >= r["scramble_from"]:
        while True:
            start = [rng.randint(0, 1) for _ in range(bits)]
            if from_bits(start) != target:
                break
    return Level(number=number, difficulty=difficulty, bits=bits, target=target, start=start,
                 show_values=number <= r["values_until"], show_total=r["total"], penalty=r["penalty"])


def score_for(seconds_left):
    return max(0, int(seconds_left)) * POINTS_PER_SECOND


def show_plan(number, rng=None):
    """The fireworks programme for a level: mortars, shells and their sizes."""
    rng = rng or random.Random(number)
    mortars = min(9, 1 + (number - 1) // 11)
    shells = min(40, 2 + number // 3 + (6 if number % 10 == 0 else 0))
    size = 0.75 + 0.85 * (number - 1) / (LEVELS - 1)
    kinds = [k for lv, k in SHELL_UNLOCKS if number >= lv]
    duration = 3.2 + number * 0.055
    plan = []
    for i in range(shells):
        t = (i / max(1, shells - 1)) * duration * 0.82 if shells > 1 else 0.0
        t += rng.uniform(-0.12, 0.12)
        plan.append((max(0.0, t), rng.randrange(mortars), rng.choice(kinds),
                     size * rng.uniform(0.85, 1.15)))
    if number % 10 == 0 or number == LEVELS:
        # a finale: every mortar fires together at the end
        for m in range(mortars):
            plan.append((duration * 0.9 + rng.uniform(0, 0.25), m, rng.choice(kinds), size * 1.25))
    plan.sort()
    return {"mortars": mortars, "plan": plan, "duration": duration + 2.5, "size": size}
