"""
测试牌力评估功能
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_environment import RLEnvironment
from cards import Card, CardPattern, CardType, Suit


class TestCardStrength(unittest.TestCase):
    """测试牌力评估功能"""
    
    def setUp(self):
        """测试前准备"""
        self.env = RLEnvironment()
        self.env.reset()
    
    def test_single_card_strength(self):
        """测试单张牌力评估"""
        # 创建不同点数的单张牌
        single_low = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '3')], 3)
        single_mid = CardPattern(CardType.SINGLE, [Card(Suit.HEART, '8')], 8)
        single_high = CardPattern(CardType.SINGLE, [Card(Suit.DIAMOND, 'A')], 14)
        single_2 = CardPattern(CardType.SINGLE, [Card(Suit.CLUB, '2')], 15)
        
        # 测试牌力判断
        is_low_strongest = self.env._is_card_strongest(single_low)
        is_mid_strongest = self.env._is_card_strongest(single_mid)
        is_high_strongest = self.env._is_card_strongest(single_high)
        is_2_strongest = self.env._is_card_strongest(single_2)
        
        # 验证返回值类型
        self.assertIsInstance(is_low_strongest, bool)
        self.assertIsInstance(is_mid_strongest, bool)
        self.assertIsInstance(is_high_strongest, bool)
        self.assertIsInstance(is_2_strongest, bool)
    
    def test_pair_card_strength(self):
        """测试对子牌力评估"""
        # 创建对子牌型
        pair_low = CardPattern(CardType.PAIR, [Card(Suit.SPADE, '4'), Card(Suit.HEART, '4')], 4)
        pair_high = CardPattern(CardType.PAIR, [Card(Suit.CLUB, 'K'), Card(Suit.DIAMOND, 'K')], 13)
        
        # 测试牌力判断
        is_pair_low_strongest = self.env._is_card_strongest(pair_low)
        is_pair_high_strongest = self.env._is_card_strongest(pair_high)
        
        # 验证返回值类型
        self.assertIsInstance(is_pair_low_strongest, bool)
        self.assertIsInstance(is_pair_high_strongest, bool)
    
    def test_bomb_card_strength(self):
        """测试炸弹牌力评估"""
        # 创建炸弹牌型
        bomb_7 = CardPattern(CardType.BOMB, 
                            [Card(Suit.SPADE, '7'), Card(Suit.HEART, '7'), 
                             Card(Suit.CLUB, '7'), Card(Suit.DIAMOND, '7')], 7)
        
        bomb_k = CardPattern(CardType.BOMB, 
                            [Card(Suit.SPADE, 'K'), Card(Suit.HEART, 'K'), 
                             Card(Suit.CLUB, 'K'), Card(Suit.DIAMOND, 'K')], 13)
        
        bomb_a = CardPattern(CardType.BOMB, 
                            [Card(Suit.SPADE, 'A'), Card(Suit.HEART, 'A'), 
                             Card(Suit.CLUB, 'A'), Card(Suit.DIAMOND, 'A')], 14)
        
        # 测试炸弹牌力
        is_7_strongest = self.env._is_card_strongest(bomb_7)
        is_k_strongest = self.env._is_card_strongest(bomb_k)
        is_a_strongest = self.env._is_card_strongest(bomb_a)
        
        # 验证返回值类型
        self.assertIsInstance(is_7_strongest, bool)
        self.assertIsInstance(is_k_strongest, bool)
        self.assertIsInstance(is_a_strongest, bool)
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试空牌型
        is_empty_strongest = self.env._is_card_strongest(None)
        self.assertIsInstance(is_empty_strongest, bool)
        
        # 测试无法估计对手手牌的情况
        # 临时清空remaining_cards来模拟这种情况
        self.env.engine.remaining_cards = []
        single_card = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '5')], 5)
        is_no_info_strongest = self.env._is_card_strongest(single_card)
        self.assertIsInstance(is_no_info_strongest, bool)


if __name__ == '__main__':
    unittest.main()