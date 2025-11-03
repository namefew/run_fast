"""
测试强化学习环境的增强功能
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_environment import RLEnvironment
from game import GameEngine
from cards import Card, CardPattern, CardType, Suit
import numpy as np


class TestRLEnhancements(unittest.TestCase):
    """测试强化学习环境的增强功能"""
    
    def test_enhanced_features(self):
        """测试增强的RL功能"""
        # 创建环境
        env = RLEnvironment()
        state = env.reset()
        
        # 验证状态维度
        self.assertIsInstance(state, (list, np.ndarray))
        self.assertGreater(len(state), 0)
        
        # 测试牌力评估功能
        # 创建一个单张牌型进行测试
        single_card = Card(Suit.SPADE, 'A')
        single_pattern = CardPattern(CardType.SINGLE, [single_card], 14)  # A的点数是14
        
        # 检查是否为最大牌
        is_strongest = env._is_card_strongest(single_pattern)
        self.assertIsInstance(is_strongest, bool)
        
        # 计算被管住的概率
        blocking_prob = env._calculate_blocking_probability(single_pattern)
        self.assertIsInstance(blocking_prob, float)
        self.assertGreaterEqual(blocking_prob, 0.0)
        self.assertLessEqual(blocking_prob, 1.0)
        
        # 测试奖励计算
        reward = env._calculate_reward(single_pattern)
        self.assertIsInstance(reward, float)
    
    def test_edge_cases(self):
        """测试边界情况"""
        env = RLEnvironment()
        env.reset()
        
        # 测试空牌型
        is_strongest = env._is_card_strongest(None)
        self.assertIsInstance(is_strongest, bool)
        
        blocking_prob = env._calculate_blocking_probability(None)
        self.assertIsInstance(blocking_prob, float)
        self.assertGreaterEqual(blocking_prob, 0.0)
        self.assertLessEqual(blocking_prob, 1.0)
        
        # 测试未知牌型类型
        unknown_card = Card(Suit.SPADE, '6')
        unknown_pattern = CardPattern(CardType.SINGLE, [unknown_card], 6)
        unknown_pattern.type = None  # 模拟未知类型
        
        blocking_prob = env._calculate_blocking_probability(unknown_pattern)
        self.assertIsInstance(blocking_prob, float)
        self.assertGreaterEqual(blocking_prob, 0.0)
        self.assertLessEqual(blocking_prob, 1.0)


if __name__ == "__main__":
    unittest.main()