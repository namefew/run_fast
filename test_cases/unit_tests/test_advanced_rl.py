"""
测试强化学习环境的高级功能
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_environment import RLEnvironment
from game import GameEngine
from cards import Card, CardPattern, CardType, Suit


class TestAdvancedRL(unittest.TestCase):
    """测试强化学习环境的高级功能"""
    
    def test_card_strength_estimation(self):
        """测试牌力评估功能"""
        env = RLEnvironment()
        env.reset()
        
        # 模拟已经出了3张A的情况
        for i in range(3):
            fake_card = Card(Suit.SPADE, 'A')
            env.engine.game_history.append({
                'player': 0,
                'cards': [fake_card],
                'pattern': None,
                'hand_before': [],
                'opponent_hand_size': 16,
                'is_first_round': True
            })
        
        # 创建一个A的牌型
        ace_card = Card(Suit.DIAMOND, 'A')
        ace_pattern = CardPattern(CardType.SINGLE, [ace_card], 14)
        
        # 检查是否为最大牌
        is_strongest = env._is_card_strongest(ace_pattern)
        # 验证返回值类型
        self.assertIsInstance(is_strongest, bool)
        
        # 测试只出了2张A的情况
        env2 = RLEnvironment()
        env2.reset()
        
        for i in range(2):
            fake_card = Card(Suit.SPADE, 'A')
            env2.engine.game_history.append({
                'player': 0,
                'cards': [fake_card],
                'pattern': None,
                'hand_before': [],
                'opponent_hand_size': 16,
                'is_first_round': True
            })
        
        is_strongest2 = env2._is_card_strongest(ace_pattern)
        # 验证返回值类型
        self.assertIsInstance(is_strongest2, bool)
    
    def test_blocking_probability(self):
        """测试管牌概率计算"""
        env = RLEnvironment()
        env.reset()
        
        # 设置对手手牌数
        env.engine.state.players[1] = [Card(Suit.HEART, '4')] * 10  # 对手有10张牌
        
        # 测试不同牌型的管牌概率
        single_card = Card(Suit.SPADE, '7')
        single_pattern = CardPattern(CardType.SINGLE, [single_card], 7)
        
        pair_card1 = Card(Suit.SPADE, '8')
        pair_card2 = Card(Suit.HEART, '8')
        pair_pattern = CardPattern(CardType.PAIR, [pair_card1, pair_card2], 8)
        
        bomb_cards = [Card(Suit.SPADE, '9'), Card(Suit.HEART, '9'), Card(Suit.CLUB, '9'), Card(Suit.DIAMOND, '9')]
        bomb_pattern = CardPattern(CardType.BOMB, bomb_cards, 9)
        
        single_prob = env._calculate_blocking_probability(single_pattern)
        pair_prob = env._calculate_blocking_probability(pair_pattern)
        bomb_prob = env._calculate_blocking_probability(bomb_pattern)
        
        # 验证返回值类型
        self.assertIsInstance(single_prob, float)
        self.assertIsInstance(pair_prob, float)
        self.assertIsInstance(bomb_prob, float)
        
        # 验证概率在合理范围内
        self.assertGreaterEqual(single_prob, 0.0)
        self.assertLessEqual(single_prob, 1.0)
        self.assertGreaterEqual(pair_prob, 0.0)
        self.assertLessEqual(pair_prob, 1.0)
        self.assertGreaterEqual(bomb_prob, 0.0)
        self.assertLessEqual(bomb_prob, 1.0)
    
    def test_reward_calculation(self):
        """测试奖励计算"""
        env = RLEnvironment()
        env.reset()
        
        # 测试普通单张
        single_card = Card(Suit.SPADE, '5')
        single_pattern = CardPattern(CardType.SINGLE, [single_card], 5)
        
        # 测试小点数单张（应该有额外奖励）
        small_single_card = Card(Suit.SPADE, '4')
        small_single_pattern = CardPattern(CardType.SINGLE, [small_single_card], 4)
        
        # 测试炸弹
        bomb_cards = [Card(Suit.SPADE, 'K'), Card(Suit.HEART, 'K'), Card(Suit.CLUB, 'K'), Card(Suit.DIAMOND, 'K')]
        bomb_pattern = CardPattern(CardType.BOMB, bomb_cards, 13)
        
        reward1 = env._calculate_reward(single_pattern)
        reward2 = env._calculate_reward(small_single_pattern)
        reward3 = env._calculate_reward(bomb_pattern)
        
        # 验证返回值类型
        self.assertIsInstance(reward1, float)
        self.assertIsInstance(reward2, float)
        self.assertIsInstance(reward3, float)
    
    def test_opponent_estimation(self):
        """测试对手手牌估计"""
        env = RLEnvironment()
        env.reset()
        
        # 设置对手手牌
        env.engine.state.players[1] = [Card(Suit.HEART, '6'), Card(Suit.CLUB, '7')]
        
        estimated_cards = env._estimate_opponent_cards()
        # 验证返回值类型
        self.assertIsInstance(estimated_cards, list)


if __name__ == '__main__':
    unittest.main()