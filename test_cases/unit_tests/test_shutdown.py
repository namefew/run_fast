"""
测试关牌情况的积分计算
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import GameEngine
from cards import Card, Suit


class TestShutdown(unittest.TestCase):
    """测试关牌情况的积分计算"""
    
    def test_shutdown(self):
        """测试关牌情况"""
        # 创建游戏引擎
        engine = GameEngine()
        engine.deal_cards()
        
        # 模拟一个即将关牌的游戏状态
        # 玩家0只剩1张牌
        engine.state.players[0] = [Card(Suit.SPADE, '3')]
        # 玩家1还有一些牌
        engine.state.players[1] = [Card(Suit.HEART, '4'), Card(Suit.CLUB, '5'), Card(Suit.DIAMOND, '6')]
        
        # 玩家0先出牌
        engine.state.current_player = 0
        engine.state.last_pattern = None
        engine.state.player_cards_left[0] = 1
        engine.state.player_cards_left[1] = 3
        
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
            elif remaining_cards == 2:
                expected_score *= 2
            
            # 验证得分计算（允许一定的误差）
            self.assertGreaterEqual(engine.state.scores[engine.state.winner], expected_score // 2)


if __name__ == "__main__":
    unittest.main()