import random

from bitfuse import levels


def test_bits_round_trip():
    for bits in range(1, 17):
        for value in (0, 1, (1 << bits) - 1, (1 << bits) // 3):
            assert levels.from_bits(levels.to_bits(value, bits)) == value
    assert levels.to_bits(5, 4) == [0, 1, 0, 1]


def test_switch_counts_follow_the_difficulty():
    for diff, rule in levels.RULES.items():
        counts = [levels.bits_for(n, diff) for n in range(1, levels.LEVELS + 1)]
        assert counts[0] == rule["min_bits"]
        assert counts[-1] == rule["max_bits"]
        assert counts == sorted(counts), "switch count must never go down"


def test_targets_are_valid_and_grow():
    rng = random.Random(1)
    for diff in levels.DIFFICULTIES:
        averages = []
        for n in range(1, levels.LEVELS + 1):
            values = []
            for _ in range(20):
                lv = levels.generate(n, diff, rng)
                assert 1 <= lv.target < (1 << lv.bits)
                assert len(lv.start) == lv.bits
                if lv.start != [0] * lv.bits:
                    assert levels.from_bits(lv.start) != lv.target, "scrambled start must not already be solved"
                values.append(lv.target)
            averages.append(sum(values) / len(values))
        # numbers get larger: each block of ten levels averages more than the one before
        blocks = [sum(averages[i:i + 10]) / 10 for i in range(0, levels.LEVELS, 10)]
        assert blocks == sorted(blocks)


def test_hard_rules():
    rng = random.Random(3)
    assert levels.generate(20, "hard", rng).show_values
    assert not levels.generate(21, "hard", rng).show_values
    assert levels.generate(1, "easy", rng).show_total
    assert not levels.generate(1, "medium", rng).show_total
    assert levels.generate(40, "medium", rng).start == [0] * levels.bits_for(40, "medium")


def test_score_is_100_points_per_second():
    assert levels.score_for(99) == 9900
    assert levels.score_for(42.7) == 4200
    assert levels.score_for(-3) == 0


def test_fireworks_get_bigger():
    small, big = levels.show_plan(1), levels.show_plan(100)
    assert big["mortars"] > small["mortars"]
    assert len(big["plan"]) > len(small["plan"])
    assert big["size"] > small["size"]
    assert all(m < big["mortars"] for _t, m, _k, _s in big["plan"])
