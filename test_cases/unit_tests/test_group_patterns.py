"""
测试牌型分组功能
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from game import GameEngine
from cards import Card, Suit, CardType, CardPattern


class TestGroupPatterns(unittest.TestCase):
    
    def setUp(self):
        """初始化测试环境"""
        self.engine = GameEngine()
    
    def test_simple_hand(self):
        """测试简单手牌分组"""
        # 手牌: 3♠, 3♥, 4♠
        hand = [
            Card(Suit.SPADE, '3'),
            Card(Suit.HEART, '3'),
            Card(Suit.SPADE, '4')
        ]
        
        # 生成所有可能的牌型
        patterns = []
        self.engine._generate_all_patterns(hand, patterns)
        self.assertGreater(len(patterns), 0, "应该生成至少一个牌型")
        
        # 测试分组
        groups = self.engine.group_patterns_into_hands(hand, patterns)
        self.assertGreater(len(groups), 0, "应该生成至少一个分组")
        
        # 检查分组是否完整覆盖手牌
        for group in groups:
            group_cards = []
            for pattern in group:
                group_cards.extend(pattern.cards)
            
            # 检查牌数是否匹配
            self.assertEqual(len(group_cards), len(hand), "分组应该完整覆盖手牌")
    
    def test_pair_hand(self):
        """测试对子手牌分组"""
        # 手牌: 3♠, 3♥
        hand = [
            Card(Suit.SPADE, '3'),
            Card(Suit.HEART, '3')
        ]
        
        # 生成所有可能的牌型
        patterns = []
        self.engine._generate_all_patterns(hand, patterns)
        self.assertEqual(len(patterns), 2, "应该生成两个牌型（对子和单张）")
        
        # 测试分组
        groups = self.engine.group_patterns_into_hands(hand, patterns)
        self.assertEqual(len(groups), 1, "应该生成一个完整分组")
        self.assertEqual(len(groups[0]), 1, "分组应该包含一个牌型")
        self.assertEqual(groups[0][0].type, CardType.PAIR, "分组中的牌型应该是对子")
    
    def test_straight_hand(self):
        """测试顺子手牌分组"""
        # 手牌: 3♠, 4♥, 5♦, 6♣, 7♠
        hand = [
            Card(Suit.SPADE, '3'),
            Card(Suit.HEART, '4'),
            Card(Suit.DIAMOND, '5'),
            Card(Suit.CLUB, '6'),
            Card(Suit.SPADE, '7')
        ]
        
        # 生成所有可能的牌型
        patterns = []
        self.engine._generate_all_patterns(hand, patterns)
        self.assertGreater(len(patterns), 0, "应该生成至少一个牌型")
        
        # 应该包含一个顺子
        has_straight = any(pattern.type == CardType.STRAIGHT for pattern in patterns)
        self.assertTrue(has_straight, "应该生成顺子牌型")
        
        # 测试分组
        groups = self.engine.group_patterns_into_hands(hand, patterns)
        self.assertGreater(len(groups), 0, "应该生成至少一个分组")
    
    def test_double_straight_hand(self):
        """测试连对手牌分组"""
        # 手牌: 3♠, 3♥, 4♦, 4♣
        hand = [
            Card(Suit.SPADE, '3'),
            Card(Suit.HEART, '3'),
            Card(Suit.DIAMOND, '4'),
            Card(Suit.CLUB, '4')
        ]
        
        # 生成所有可能的牌型
        patterns = []
        self.engine._generate_all_patterns(hand, patterns)
        self.assertGreater(len(patterns), 0, "应该生成至少一个牌型")
        
        # 应该包含一个连对
        has_double_straight = any(pattern.type == CardType.DOUBLE_STRAIGHT for pattern in patterns)
        self.assertTrue(has_double_straight, "应该生成连对牌型")
        
        # 测试分组
        groups = self.engine.group_patterns_into_hands(hand, patterns)
        self.assertGreater(len(groups), 0, "应该生成至少一个分组")
    
    def test_complex_hand(self):
        """测试复杂手牌分组"""
        # 手牌: 3, 4, 7, 9, J, J, Q, Q, K, K, A, A
        hand = [
            Card(Suit.SPADE, '3'),
            Card(Suit.HEART, '4'),
            Card(Suit.SPADE, '7'),
            Card(Suit.SPADE, '9'),
            Card(Suit.SPADE, 'J'),
            Card(Suit.HEART, 'J'),
            Card(Suit.SPADE, 'Q'),
            Card(Suit.HEART, 'Q'),
            Card(Suit.SPADE, 'K'),
            Card(Suit.HEART, 'K'),
            Card(Suit.SPADE, 'A'),
            Card(Suit.HEART, 'A')
        ]
        
        # 生成所有可能的牌型
        patterns = []
        self.engine._generate_all_patterns(hand, patterns)
        self.assertGreater(len(patterns), 0, "应该生成至少一个牌型")
        
        # 测试分组
        groups = self.engine.group_patterns_into_hands(hand, patterns)
        self.assertGreater(len(groups), 0, "应该生成至少一个分组")
        
        # 检查分组是否完整覆盖手牌
        for group in groups:
            group_cards = []
            for pattern in group:
                group_cards.extend(pattern.cards)
            
            # 检查牌数是否匹配
            self.assertEqual(len(group_cards), len(hand), "分组应该完整覆盖手牌")
    
    def test_airplane_hand(self):
        """测试飞机手牌分组"""
        # 手牌: 3♠, 3♥, 3♦, 4♣, 4♠, 4♥
        hand = [
            Card(Suit.SPADE, '3'),
            Card(Suit.HEART, '3'),
            Card(Suit.DIAMOND, '3'),
            Card(Suit.CLUB, '4'),
            Card(Suit.SPADE, '4'),
            Card(Suit.HEART, '4')
        ]
        
        # 生成所有可能的牌型
        patterns = []
        self.engine._generate_all_patterns(hand, patterns)
        self.assertGreater(len(patterns), 0, "应该生成至少一个牌型")
        
        # 应该包含一个飞机
        has_airplane = any(pattern.type == CardType.AIRPLANE for pattern in patterns)
        self.assertTrue(has_airplane, "应该生成飞机牌型")
        
        # 测试分组
        groups = self.engine.group_patterns_into_hands(hand, patterns)
        self.assertGreater(len(groups), 0, "应该生成至少一个分组")
    
    def test_bomb_hand(self):
        """测试炸弹手牌分组"""
        # 手牌: 3♠, 3♥, 3♦, 3♣
        hand = [
            Card(Suit.SPADE, '3'),
            Card(Suit.HEART, '3'),
            Card(Suit.DIAMOND, '3'),
            Card(Suit.CLUB, '3')
        ]
        
        # 生成所有可能的牌型
        patterns = []
        self.engine._generate_all_patterns(hand, patterns)
        self.assertGreater(len(patterns), 0, "应该生成至少一个牌型")
        
        # 应该包含一个炸弹
        has_bomb = any(pattern.type == CardType.BOMB for pattern in patterns)
        self.assertTrue(has_bomb, "应该生成炸弹牌型")
        
        # 测试分组
        groups = self.engine.group_patterns_into_hands(hand, patterns)
        self.assertGreater(len(groups), 0, "应该生成至少一个分组")


if __name__ == '__main__':
    unittest.main()