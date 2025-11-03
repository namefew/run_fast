"""
工具函数模块
"""

from typing import List, Dict, Tuple
from cards import Card, CardPattern


def sort_cards(cards: List[Card]) -> List[Card]:
    """排序牌"""
    return sorted(cards)


def count_cards_by_point(cards: List[Card]) -> Dict[int, int]:
    """统计各点数牌的数量"""
    counts = {}
    for card in cards:
        counts[card.point] = counts.get(card.point, 0) + 1
    return counts


def find_patterns_in_hand(hand: List[Card]) -> List[CardPattern]:
    """在手牌中查找所有可能的牌型组合"""
    # 这是一个复杂的功能，需要实现所有牌型的识别
    # 这里只是一个简单的占位实现
    patterns = []
    return patterns


def evaluate_hand_strength(hand: List[Card]) -> float:
    """评估手牌强度"""
    # 这里可以实现一个复杂的手牌强度评估算法
    # 简单实现：返回手牌数量的倒数（牌越少强度越高）
    return 1.0 / len(hand) if hand else 0.0