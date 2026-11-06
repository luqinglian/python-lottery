# -*- coding: utf-8 -*-
"""lottery.py 的单元测试：python3 -m unittest -v"""

import unittest
from collections import Counter

from lottery import Participant, draw, parse_participants


class ParseParticipantsTest(unittest.TestCase):
    def test_plain_names(self):
        people = parse_participants("张三,李四, 王五")
        self.assertEqual([p.name for p in people], ["张三", "李四", "王五"])
        self.assertTrue(all(p.weight == 1.0 for p in people))

    def test_newlines_and_weights(self):
        people = parse_participants("张三:3\n李四\n王五:0.5")
        self.assertEqual([p.weight for p in people], [3.0, 1.0, 0.5])

    def test_empty_participants_raises(self):
        with self.assertRaises(ValueError):
            parse_participants("  , \n ")

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            parse_participants("张三,张三")

    def test_bad_weight_raises(self):
        for bad in ("张三:abc", "张三:0", "张三:-1", "张三:"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_participants(bad)


class DrawTest(unittest.TestCase):
    def setUp(self):
        self.people = parse_participants("A,B,C,D,E")

    def test_draws_requested_count(self):
        winners = draw(self.people, 3, seed=1)
        self.assertEqual(len(winners), 3)

    def test_unique_by_default(self):
        winners = draw(self.people, 5, seed=7)
        self.assertEqual(len({w.name for w in winners}), 5)

    def test_allow_repeat(self):
        winners = draw(self.people, 20, seed=3, unique=False)
        self.assertEqual(len(winners), 20)

    def test_same_seed_same_result(self):
        first = [w.name for w in draw(self.people, 3, seed=2024)]
        second = [w.name for w in draw(self.people, 3, seed=2024)]
        self.assertEqual(first, second)

    def test_different_seed_can_differ(self):
        results = {tuple(w.name for w in draw(self.people, 3, seed=s)) for s in range(20)}
        self.assertGreater(len(results), 1)

    def test_too_many_winners_raises(self):
        with self.assertRaises(ValueError):
            draw(self.people, 6)

    def test_zero_or_negative_count_raises(self):
        for count in (0, -3):
            with self.subTest(count=count), self.assertRaises(ValueError):
                draw(self.people, count)

    def test_empty_pool_raises(self):
        with self.assertRaises(ValueError):
            draw([], 1)

    def test_weight_bias(self):
        """权重大的人应当更常中奖。"""
        people = [Participant("重", 9.0), Participant("轻", 1.0)]
        counter = Counter()
        for seed in range(2000):
            counter[draw(people, 1, seed=seed)[0].name] += 1
        self.assertGreater(counter["重"], counter["轻"] * 3)

    def test_returns_participant_objects(self):
        winners = draw(self.people, 1, seed=0)
        self.assertIsInstance(winners[0], Participant)


if __name__ == "__main__":
    unittest.main(verbosity=2)
