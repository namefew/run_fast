"""
跑得快游戏的牌类和牌型处理模块
"""

import random
from typing import List, Dict, Tuple, Optional
from enum import Enum


class Suit(Enum):
    """花色枚举"""
    SPADE = "♠"
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"


class Card:
    """牌类"""
    # 牌点数映射，3最小，2最大
    POINTS = {
        '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15
    }

    def __init__(self, suit: Suit, rank: str):
        self.suit = suit
        self.rank = rank
        self.point = self.POINTS[rank]

    def __str__(self):
        return f"{self.suit.value}{self.rank}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.point == other.point and self.suit == other.suit

    def __lt__(self, other):
        # 特殊处理：2比3大
        if self.point == 15 and other.point == 3:
            return False
        if self.point == 3 and other.point == 15:
            return True
        return self.point < other.point
    
    def __hash__(self):
        return hash((self.suit, self.rank, self.point))


class CardType(Enum):
    """牌型枚举"""
    SINGLE = 1      # 单张
    PAIR = 2        # 对子
    THREE_WITH_TWO = 3  # 三带二
    STRAIGHT = 4    # 顺子
    DOUBLE_STRAIGHT = 5  # 连对
    AIRPLANE = 6    # 飞机
    AIRPLANE_WITH_WINGS = 7  # 飞机带翅膀
    BOMB = 8        # 炸弹
    FOUR_WITH_THREE = 9  # 四带三


class CardPattern:
    """牌型类"""
    def __init__(self, card_type: CardType, cards: List[Card], main_point: int = 0):
        self.type = card_type
        self.cards = sorted(cards)
        self.main_point = main_point  # 主牌点数，用于比较大小
        self.card_count = len(cards)

    def __str__(self):
        return f"{self.type.name}({[str(card) for card in self.cards]})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.type == other.type and self.main_point == other.main_point
    
    def __hash__(self):
        return hash((self.type, self.main_point,self.card_count))


def create_deck() -> List[Card]:
    """创建一副跑得快的牌（48张）"""
    # 去掉大小王、三个2（保留黑桃2）和黑桃A
    ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
    deck = []
    
    for rank in ranks:
        for suit in Suit:
            # 跳过黑桃A和三个2（红桃2、方片2、梅花2）
            if rank == 'A' and suit == Suit.SPADE:
                continue
            if rank == '2' and suit != Suit.SPADE:
                continue
            deck.append(Card(suit, rank))
    
    return deck


def detect_card_type(cards: List[Card]) -> Optional[CardPattern]:
    """识别牌型"""
    if not cards:
        return None

    cards = sorted(cards)
    card_count = len(cards)

    # 单张
    if card_count == 1:
        return CardPattern(CardType.SINGLE, cards, cards[0].point)

    # 对子
    if card_count == 2 and cards[0].point == cards[1].point:
        return CardPattern(CardType.PAIR, cards, cards[0].point)
        # 炸弹（4张相同或3张A）
    if card_count == 4:
        if all(card.point == cards[0].point for card in cards):
            return CardPattern(CardType.BOMB, cards, cards[0].point)

    if card_count == 3:
        if all(card.point == 14 for card in cards):  # 3张A
            return CardPattern(CardType.BOMB, cards, 14)  # A的点数是14
            
    # 三带二 (必须正好是5张牌)
    if 3<=card_count <= 5:
        points = [card.point for card in cards]
        point_counts = {}
        for point in points:
            point_counts[point] = point_counts.get(point, 0) + 1

        # 检查是否有三张相同点数的牌
        if 3 in point_counts.values():
            # 找到三张相同的点数作为主点数
            main_point = [point for point, count in point_counts.items() if count == 3][0]
            return CardPattern(CardType.THREE_WITH_TWO, cards, main_point)

    # 顺子（5张及以上连续单牌）
    if card_count >= 5:
        points = [card.point for card in cards]
        points.sort()
        # 检查是否连续
        is_straight = True
        # 额外检查：顺子中不能包含2（因为2是最大的牌）
        if 15 in points:  # 2的点数是15
            is_straight = False

        # 额外检查：A不能作为顺子的最小牌（即不能作为1使用）
        if points[0] == 14:  # A是第一张牌（最小的）
            is_straight = False
        for i in range(1, len(points)):
            # 普通连续性检查
            if points[i] - points[i - 1] != 1:
                is_straight = False
                break

        if is_straight and len(set(points)) == len(points):  # 确保没有重复点数
            return CardPattern(CardType.STRAIGHT, cards, points[0])  # 主牌改回最小的牌

    # 连对（2个及以上连续对子）
    if card_count >= 4 and card_count % 2 == 0:
        points = [card.point for card in cards]
        point_counts = {}
        for point in points:
            point_counts[point] = point_counts.get(point, 0) + 1

        # 检查是否都是对子
        if all(count == 2 for count in point_counts.values()):
            unique_points = sorted(point_counts.keys())
            # 额外检查：连对中不能包含2（因为2是最大的牌）
            is_consecutive = True
            if 15 in unique_points:  # 2的点数是15
                is_consecutive =  False
            # 额外检查：A不能作为连对的最小牌
            if unique_points[0] == 14:  # A是最小的
                is_consecutive = False
            for i in range(1, len(unique_points)):
                if unique_points[i] - unique_points[i - 1] != 1:
                    is_consecutive = False
                    break
            if is_consecutive:
                return CardPattern(CardType.DOUBLE_STRAIGHT, cards, unique_points[0])
                
    # 四带三
    if card_count >= 4:
        points = [card.point for card in cards]
        point_counts = {}
        for point in points:
            point_counts[point] = point_counts.get(point, 0) + 1

        values_list = list(point_counts.values())
        has_four = 4 in values_list
        if has_four:
            four_point = [point for point, count in point_counts.items() if count == 4][0]
            return CardPattern(CardType.FOUR_WITH_THREE, cards, four_point)
            
    # 飞机（2个及以上连续三同张）
    if card_count >= 6 and card_count % 3 == 0:
        points = [card.point for card in cards]
        point_counts = {}
        for point in points:
            point_counts[point] = point_counts.get(point, 0) + 1

        # 检查是否都是三同张
        if all(count == 3 for count in point_counts.values()):
            unique_points = sorted(point_counts.keys())
            is_consecutive = True
            # 额外检查：飞机中不能包含2（因为2是最大的牌）
            if 15 in unique_points:  # 2的点数是15
                is_consecutive = False

            # 额外检查：A不能作为飞机的最小牌
            if unique_points[0] == 14:  # A是最小的
                is_consecutive = False
            # 检查点数是否连续
            for i in range(1, len(unique_points)):
                if unique_points[i] - unique_points[i - 1] != 1:
                    is_consecutive = False
                    break

            if is_consecutive:
                return CardPattern(CardType.AIRPLANE, cards, unique_points[0])

    # 飞机带翅膀
    if card_count >= 7:
        points = [card.point for card in cards]
        point_counts = {}
        for point in points:
            point_counts[point] = point_counts.get(point, 0) + 1

        # 统计三同张的数量
        triple_points = [point for point, count in point_counts.items() if count == 3]
        if len(triple_points) >= 2:
            # 检查三同张是否连续
            triple_points.sort()
            is_consecutive = True
            for i in range(1, len(triple_points)):
                if triple_points[i] - triple_points[i - 1] != 1:
                    is_consecutive = False
                    break

            if is_consecutive:
                # 需要带的牌数 = 三同张数量 * 2
                wings_needed = len(triple_points) * 2
                wings_count = sum(count for point, count in point_counts.items() if count < 3)

                # 检查带牌数量是否正确
                if wings_count == wings_needed:
                    return CardPattern(CardType.AIRPLANE_WITH_WINGS, cards, triple_points[0])
                else:
                    pass

    return None


def compare_patterns(pattern1: CardPattern, pattern2: CardPattern) -> bool:
    """比较两个牌型，pattern1是否能管住pattern2"""
    # 炸弹可以管任何非炸弹牌型
    if pattern1.type == CardType.BOMB and pattern2.type != CardType.BOMB:
        return True
    
    # 炸弹之间的比较
    if pattern1.type == CardType.BOMB and pattern2.type == CardType.BOMB:
        return pattern1.main_point > pattern2.main_point
    
    # 非炸弹牌型必须类型相同才能比较
    if pattern1.type != pattern2.type:
        return False

    # 三带二只能和三带二比较
    if pattern1.type == CardType.THREE_WITH_TWO:
        # 三带二只需要比较三同张的点数
        return pattern1.main_point > pattern2.main_point

    # 飞机带翅膀只能和飞机带翅膀比较
    if pattern1.type == CardType.AIRPLANE_WITH_WINGS:
        # 计算两个牌型的飞机部分三同张数量
        triple_count1 = _count_airplane_triples(pattern1)
        triple_count2 = _count_airplane_triples(pattern2)
        # 相同数量的连续三同张，比较主点数
        return triple_count1 == triple_count2 and pattern1.main_point > pattern2.main_point

    # 其他牌型比较需要牌数一致
    if pattern1.card_count != pattern2.card_count:
        return False
    
    # 普通比较
    return pattern1.main_point > pattern2.main_point

# 正确计算飞机带翅膀牌型中连续三同张的数量
def _count_airplane_triples(pattern: CardPattern):
    # 统计每种点数的牌数量
    points = [card.point for card in pattern.cards]
    point_counts = {}
    for point in points:
        point_counts[point] = point_counts.get(point, 0) + 1

    # 找出所有三同张点数
    triple_points = [point for point, count in point_counts.items() if count >= 3]
    triple_points.sort()

    # 找出连续的三同张序列（飞机部分）
    if not triple_points:
        return 0

    max_consecutive_count = 1
    current_consecutive_count = 1

    for i in range(1, len(triple_points)):
        if triple_points[i] - triple_points[i - 1] == 1:
            current_consecutive_count += 1
            max_consecutive_count = max(max_consecutive_count, current_consecutive_count)
        else:
            current_consecutive_count = 1

    return max_consecutive_count