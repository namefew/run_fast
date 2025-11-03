"""
测试简单的游戏流程
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import GameEngine


class TestSimpleGame(unittest.TestCase):
    """测试简单游戏流程"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = GameEngine()
    
    def test_game_initialization(self):
        """测试游戏初始化"""
        self.engine.deal_cards()
        self.assertEqual(len(self.engine.state.players[0]), 16)
        self.assertEqual(len(self.engine.state.players[1]), 16)
        self.assertFalse(self.engine.state.game_over)
    
    def test_simple_game_play(self):
        """测试简单游戏流程"""
        self.engine.deal_cards()
        
        # 简单游戏循环直到结束
        while not self.engine.state.game_over:
            valid_patterns = self.engine.get_valid_patterns(self.engine.state.current_player)
            if valid_patterns:
                pattern = valid_patterns[0]
                self.engine.play_cards(self.engine.state.current_player, pattern.cards)
            else:
                self.engine.pass_turn(self.engine.state.current_player)
        
        # 验证游戏结束状态
        self.assertTrue(self.engine.state.game_over)
        self.assertIn(self.engine.state.winner, [0, 1])
        self.assertNotEqual(self.engine.state.scores[0], 0)
        self.assertNotEqual(self.engine.state.scores[1], 0)


if __name__ == '__main__':
    unittest.main()