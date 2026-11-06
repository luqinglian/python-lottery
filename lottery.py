#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python 抽奖小程序。

一个零依赖的命令行抽奖工具，支持：
  * 从名单中抽取指定数量的中奖者
  * 中奖去重（默认）或允许重复中奖
  * 按权重抽奖（"张三:3,李四:1" 表示张三中奖概率是李四的 3 倍）
  * 固定随机种子，结果可复现
  * 文本 / JSON 两种输出

用法示例：
    python3 lottery.py -p "张三,李四,王五,赵六" -n 2
    python3 lottery.py -p "张三:3,李四:1,王五:1" -n 1 --seed 42
    python3 lottery.py -f names.txt -n 3 --json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class Participant:
    """一个参与者。weight 越大，中奖概率越高。"""

    name: str
    weight: float = 1.0


def parse_participants(text: str) -> List[Participant]:
    """把名单文本解析成 Participant 列表。

    支持逗号或换行分隔，名字后可跟 ":权重"，例如：
        "张三,李四:2,王五"
    权重必须大于 0，缺省为 1。
    """
    participants: List[Participant] = []
    seen = set()
    for raw in text.replace("\n", ",").split(","):
        item = raw.strip()
        if not item:
            continue
        name, sep, weight_text = item.partition(":")
        name = name.strip()
        if not name:
            raise ValueError(f"名单中有空名字：{item!r}")
        if name in seen:
            raise ValueError(f"名单中有重复的名字：{name}")
        seen.add(name)

        weight = 1.0
        if sep:
            weight_text = weight_text.strip()
            if not weight_text:
                raise ValueError(f"权重为空：{item!r}")
            try:
                weight = float(weight_text)
            except ValueError:
                raise ValueError(f"权重不是数字：{item!r}") from None
            if weight <= 0:
                raise ValueError(f"权重必须大于 0：{item!r}")

        participants.append(Participant(name, weight))

    if not participants:
        raise ValueError("参与名单为空")
    return participants


def _pick_index(weights: Sequence[float], rng: random.Random) -> int:
    """按权重随机返回一个下标。"""
    total = sum(weights)
    point = rng.random() * total
    acc = 0.0
    for index, weight in enumerate(weights):
        acc += weight
        if point < acc:
            return index
    return len(weights) - 1  # 浮点误差兜底


def draw(
    participants: Iterable[Participant],
    count: int,
    *,
    seed: int | None = None,
    unique: bool = True,
) -> List[Participant]:
    """抽取 count 个中奖者。

    unique=True  时不会重复中奖；
    unique=False 时每轮都从完整名单里抽，可能重复。
    """
    pool = list(participants)
    if not pool:
        raise ValueError("参与名单为空")
    if count <= 0:
        raise ValueError("中奖人数必须大于 0")
    if unique and count > len(pool):
        raise ValueError(f"中奖人数 {count} 超过了参与人数 {len(pool)}")

    rng = random.Random(seed)
    winners: List[Participant] = []
    remaining = list(pool)

    for _ in range(count):
        source = remaining if unique else pool
        index = _pick_index([p.weight for p in source], rng)
        winner = source[index]
        winners.append(winner)
        if unique:
            remaining.pop(index)

    return winners


def read_participants(args: argparse.Namespace) -> List[Participant]:
    """从参数或文件读取名单。"""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            text = handle.read()
    elif args.participants:
        text = args.participants
    else:
        text = sys.stdin.read()
    return parse_participants(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lottery",
        description="Python 抽奖小程序：从名单里抽出幸运儿",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("-p", "--participants", help='名单，例如 "张三,李四:2,王五"')
    source.add_argument("-f", "--file", help="名单文件，每行一个名字（也可写 名字:权重）")
    parser.add_argument("-n", "--count", type=int, default=1, help="中奖人数，默认 1")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，指定后结果可复现")
    parser.add_argument(
        "--allow-repeat",
        action="store_true",
        help="允许重复中奖（默认不允许）",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        participants = read_participants(args)
        winners = draw(
            participants,
            args.count,
            seed=args.seed,
            unique=not args.allow_repeat,
        )
    except (ValueError, OSError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "count": len(winners),
                    "total": len(participants),
                    "seed": args.seed,
                    "winners": [p.name for p in winners],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"共 {len(participants)} 人参与，抽取 {len(winners)} 位：")
        for rank, winner in enumerate(winners, start=1):
            print(f"  {rank}. {winner.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
