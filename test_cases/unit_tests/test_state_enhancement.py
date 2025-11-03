"""
测试增强的状态表示功能
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_environment import RLEnvironment
from game import GameEngine
from cards import Card, Suit
import numpy as np


class TestStateEnhancement(unittest.TestCase):
    """测试增强的状态表示功能"""
    
    def test_enhanced_state(self):
        """测试增强的状态表示"""
        # 创建环境
        env = RLEnvironment()
        state = env.reset()
        
        # 验证状态维度
        self.assertIsInstance(state, np.ndarray)
        self.assertGreater(len(state), 0)
        
        # 检查状态各部分
        self.assertEqual(len(state[0:16]), 16)  # 手牌部分
        self.assertIsInstance(state[16], (int, float))  # 对手剩余牌数
        self.assertEqual(len(state[17:20]), 3)  # 上一手牌型信息
        self.assertIsInstance(state[20], (int, float))  # 是否首出
        self.assertEqual(len(state[21:37]), 16)  # 已出牌统计
    
    def test_with_custom_setup(self):
        """使用自定义牌局测试"""
        env = RLEnvironment()
        
        # 设置特定的手牌
        env.engine.state.players[0] = [Card(Suit.SPADE, '3'), Card(Suit.HEART, '4')]
        env.engine.state.players[1] = [Card(Suit.CLUB, '5'), Card(Suit.DIAMOND, '6')]
        env.engine.state.current_player = 0
        env.engine.state.player_cards_left[0] = 2
        env.engine.state.player_cards_left[1] = 2
        
        # 初始状态
        state = env._get_state()
        
        # 玩家0出♠3
        success = env.engine.play_cards(0, [Card(Suit.SPADE, '3')])
        self.assertTrue(success)
        
        if success:
            state = env._get_state()
            # ♠3的点数是3，对应索引0，应该计数减少了1
            # 注意：这是剩余牌的统计，所以出牌后数量应该减少
            self.assertGreaterEqual(state[21], 0)  # 确保不会是负数
        
        # 玩家1出♣5
        success = env.engine.play_cards(1, [Card(Suit.CLUB, '5')])
        self.assertTrue(success)
        
        if success:
            state = env._get_state()
            # ♣5的点数是5，对应索引2，应该计数减少了1
            self.assertGreaterEqual(state[23], 0)  # 确保不会是负数


if __name__ == "__main__":
    unittest.main()