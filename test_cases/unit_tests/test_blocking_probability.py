"""
测试改进的管牌概率计算功能
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_environment import RLEnvironment
from game import GameEngine
from cards import Card, CardPattern, CardType, Suit


class TestBlockingProbability(unittest.TestCase):
    """测试改进的管牌概率计算功能"""
    
    def test_blocking_probability_improvement(self):
        """测试改进的管牌概率计算"""
        env = RLEnvironment()
        env.reset()
        
        # 创建不同类型的牌型进行测试
        single_low = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '3')], 3)
        single_mid = CardPattern(CardType.SINGLE, [Card(Suit.HEART, '8')], 8)
        single_high = CardPattern(CardType.SINGLE, [Card(Suit.DIAMOND, 'A')], 14)
        
        # 计算管牌概率
        prob_low = env._calculate_blocking_probability(single_low)
        prob_mid = env._calculate_blocking_probability(single_mid)
        prob_high = env._calculate_blocking_probability(single_high)
        
        # 验证返回值类型
        self.assertIsInstance(prob_low, float)
        self.assertIsInstance(prob_mid, float)
        self.assertIsInstance(prob_high, float)
        
        # 验证概率在合理范围内
        self.assertGreaterEqual(prob_low, 0.0)
        self.assertLessEqual(prob_low, 1.0)
        self.assertGreaterEqual(prob_mid, 0.0)
        self.assertLessEqual(prob_mid, 1.0)
        self.assertGreaterEqual(prob_high, 0.0)
        self.assertLessEqual(prob_high, 1.0)
    
    def test_edge_cases(self):
        """测试边界情况"""
        env = RLEnvironment()
        env.reset()
        
        # 测试空牌型
        prob_empty = env._calculate_blocking_probability(None)
        self.assertIsInstance(prob_empty, float)
        
        # 测试对手手牌为0的情况
        # 模拟对手手牌为空的情况
        opponent_id = 1 - env.engine.state.current_player
        env.engine.state.players[opponent_id] = []
        
        single_card = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '5')], 5)
        prob_no_cards = env._calculate_blocking_probability(single_card)
        self.assertIsInstance(prob_no_cards, float)
    
    def test_with_known_opponent_cards(self):
        """测试在能估计对手手牌时的计算"""
        env = RLEnvironment()
        env.reset()
        
        # 获取估计的对手手牌
        estimated_cards = env._estimate_opponent_cards()
        self.assertIsInstance(estimated_cards, list)
        
        # 创建一个中等点数的牌
        mid_card = CardPattern(CardType.SINGLE, [Card(Suit.CLUB, '7')], 7)
        prob_with_estimate = env._calculate_blocking_probability(mid_card)
        self.assertIsInstance(prob_with_estimate, float)
    
    def test_compare_methods(self):
        """测试不同方法的计算结果"""
        env = RLEnvironment()
        env.reset()
        
        # 测试几种不同的牌型
        test_patterns = [
            (CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '4')], 4), "单张4"),
            (CardPattern(CardType.PAIR, [Card(Suit.HEART, '6'), Card(Suit.SPADE, '6')], 6), "对子6"),
            (CardPattern(CardType.BOMB, [Card(Suit.CLUB, 'K'), Card(Suit.DIAMOND, 'K'), 
                                       Card(Suit.HEART, 'K'), Card(Suit.SPADE, 'K')], 13), "炸弹K")
        ]
        
        for pattern, name in test_patterns:
            prob = env._calculate_blocking_probability(pattern)
            # 验证返回值类型
            self.assertIsInstance(prob, float)
            # 验证概率在合理范围内
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)


if __name__ == "__main__":
    unittest.main()