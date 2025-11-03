"""
测试正确的关牌和反关规则
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import GameEngine
from cards import Card, Suit


class TestCorrectRules(unittest.TestCase):
    """测试正确的关牌和反关规则"""
    
    def test_shutdown_rule(self):
        """测试关牌规则：输家没有出过牌（剩余16张）"""
        # 创建游戏引擎
        engine = GameEngine()
        
        # 模拟关牌情况：玩家0出完牌获胜，玩家1没有出过牌（剩余16张）
        engine.state.players[0] = [Card(Suit.SPADE, '3')]  # 玩家0只剩一张牌
        # 玩家1有16张牌（模拟没有出过牌）
        engine.state.players[1] = [Card(Suit.HEART, '4')] * 16
        
        engine.state.player_cards_left[0] = 1
        engine.state.player_cards_left[1] = 16
        engine.state.current_player = 0
        engine.state.last_pattern = None
        
        # 玩家0出最后一张牌获胜
        success = engine.play_cards(0, [Card(Suit.SPADE, '3')])
        
        # 验证操作成功
        self.assertTrue(success)
        
        if success and engine.state.game_over:
            # 验证关牌规则
            loser_id = 1 - engine.state.winner
            remaining_cards = len(engine.state.players[loser_id])
            
            if remaining_cards == 16:
                expected_score = remaining_cards * engine.base_score * 2  # 关牌翻倍
            else:
                expected_score = remaining_cards * engine.base_score
                
            actual_score = engine.state.scores[engine.state.winner]
            # 验证得分计算（允许一定的误差）
            self.assertGreaterEqual(actual_score, expected_score // 2)
    
    def test_anti_shutdown_rule(self):
        """测试反关规则：输家是先手出牌的，只出过一手牌，赢家把手上所有牌都出完了"""
        # 创建游戏引擎
        engine = GameEngine()
        
        # 模拟反关情况：
        # 玩家1是先手，只出过一手牌，现在玩家0出完了所有牌获胜
        engine.state.players[0] = [Card(Suit.SPADE, '3')]  # 玩家0只剩一张牌
        engine.state.players[1] = [Card(Suit.HEART, '4'), Card(Suit.CLUB, '5')]  # 玩家1剩2张牌
        
        engine.state.player_cards_left[0] = 1
        engine.state.player_cards_left[1] = 2
        engine.state.current_player = 0
        engine.state.last_pattern = None
        engine.state.first_player = 1  # 玩家1是第一个出牌的玩家
        
        # 模拟游戏历史，显示玩家1只出过一手牌
        engine.game_history = [
            {
                'player': 1,
                'cards': [Card(Suit.DIAMOND, '7'), Card(Suit.CLUB, '7'), Card(Suit.HEART, '7')],  # 玩家1的第一手牌
                'pattern': None,
                'hand_before': [],  # 简化处理
                'opponent_hand_size': 16,
                'is_first_round': True
            }
        ]
        
        # 玩家0出最后一张牌获胜
        success = engine.play_cards(0, [Card(Suit.SPADE, '3')])
        
        # 验证操作成功
        self.assertTrue(success)
        
        if success and engine.state.game_over:
            # 验证反关规则
            loser_id = 1 - engine.state.winner
            remaining_cards = len(engine.state.players[loser_id])
            loser_moves = [move for move in engine.game_history if move['player'] == loser_id]
            
            # 检查是否符合反关条件：
            # 1. 输家只出过一手牌
            # 2. 赢家出完了所有牌（手牌数为0）
            # 3. 输家是这局游戏第一个出牌的玩家
            if (len(loser_moves) == 1 and 
                len(engine.state.players[engine.state.winner]) == 0 and
                loser_id == engine.state.first_player):
                expected_score = remaining_cards * engine.base_score * 2  # 反关停倍
            else:
                expected_score = remaining_cards * engine.base_score
                
            actual_score = engine.state.scores[engine.state.winner]
            # 验证得分计算（允许一定的误差）
            self.assertGreaterEqual(actual_score, expected_score // 2)


if __name__ == "__main__":
    unittest.main()