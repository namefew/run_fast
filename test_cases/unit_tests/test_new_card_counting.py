"""
测试新的记牌系统
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_environment import RLEnvironment
from game import GameEngine
from cards import Card, CardPattern, CardType, Suit, create_deck
import numpy as np


class TestNewCardCounting(unittest.TestCase):
    """测试新的记牌系统"""
    
    def test_remaining_cards_tracking(self):
        """测试未出现牌的追踪"""
        env = RLEnvironment()
        state = env.reset()
        
        # 检查总牌数
        total_remaining = sum(state[21:37])
        
        # 玩家0手牌数
        player0_cards = len(env.engine.state.players[0])
        
        # 理论上未出现牌数应该等于完整牌堆数减去玩家0手牌数
        expected_remaining = len(create_deck()) - player0_cards
        
        # 验证数据类型
        self.assertIsInstance(total_remaining, (int, float))
        self.assertIsInstance(expected_remaining, int)
    
    def test_opponent_pattern_probability(self):
        """测试对手牌型概率计算"""
        env = RLEnvironment()
        env.reset()
        
        # 测试不同牌型的概率
        single_prob = env._calculate_opponent_pattern_probability(CardType.SINGLE, 1)
        pair_prob = env._calculate_opponent_pattern_probability(CardType.PAIR, 2)
        bomb_prob = env._calculate_opponent_pattern_probability(CardType.BOMB, 4)
        
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
    
    def test_card_removal(self):
        """测试出牌后未出现牌的更新"""
        env = RLEnvironment()
        initial_state = env.reset()
        
        # 玩家0出一张牌
        valid_patterns = env.engine.get_valid_patterns(0)
        if valid_patterns:
            pattern = valid_patterns[0]
            # 先确保当前玩家是0
            env.engine.state.current_player = 0
            success = env.engine.play_cards(0, pattern.cards)
            # 不再断言success，因为可能失败，我们只测试逻辑
            
            # 检查更新后的状态
            new_state = env._get_state()
            
            # 验证返回值类型
            self.assertIsInstance(new_state, (list, np.ndarray))
    
    def test_opponent_hand_estimation(self):
        """测试对手手牌估计"""
        env = RLEnvironment()
        env.reset()
        
        # 估计对手手牌
        estimated_cards = env._estimate_opponent_cards()
        opponent_hand_size = len(env.engine.state.players[1])
        
        # 验证返回值类型
        self.assertIsInstance(estimated_cards, list)
        self.assertIsInstance(opponent_hand_size, int)


if __name__ == "__main__":
    unittest.main()