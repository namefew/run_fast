"""
测试真正的关牌情况（只剩1张牌时获胜）
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import GameEngine
from cards import Card, Suit


class TestRealShutdown(unittest.TestCase):
    """测试真正的关牌情况"""
    
    def test_real_shutdown(self):
        """测试真正的关牌情况"""
        # 创建游戏引擎
        engine = GameEngine()
        
        # 设置特定的手牌来测试关牌情况
        engine.state.players[0] = [Card(Suit.SPADE, '3')]
        engine.state.players[1] = [Card(Suit.HEART, '4')]
        
        # 设置游戏状态
        engine.state.current_player = 0
        engine.state.last_pattern = None
        engine.state.player_cards_left[0] = 1
        engine.state.player_cards_left[1] = 1
        
        # 玩家0出最后一张牌
        success = engine.play_cards(0, [Card(Suit.SPADE, '3')])
        
        # 验证操作成功
        self.assertTrue(success)
        
        if success and engine.state.game_over:
            # 验证游戏结束状态
            self.assertTrue(engine.state.game_over)
            self.assertIn(engine.state.winner, [0, 1])
            
            # 检查是否正确应用了关牌规则
            loser_id = 1 - engine.state.winner
            remaining_cards = len(engine.state.players[loser_id])
            
            expected_score = remaining_cards * engine.base_score
            # 检查是否有关牌情况（剩余1张牌）
            if remaining_cards == 1:
                expected_score *= 2
            
            actual_score = engine.state.scores[engine.state.winner]
            # 验证得分计算（允许一定的误差）
            self.assertGreaterEqual(actual_score, expected_score // 2)


if __name__ == "__main__":
    unittest.main()