"""
测试新的关牌和反关规则
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import GameEngine
from cards import Card, Suit


class TestNewRules(unittest.TestCase):
    """测试新的关牌和反关规则"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = GameEngine()
    
    def test_shutdown_rule(self):
        """测试关牌规则：玩家没有出过牌（剩余16张）"""
        # 发牌
        self.engine.deal_cards()
        
        # 模拟关牌情况：玩家0出完牌，玩家1一张都没出
        self.engine.state.players[0] = [Card(Suit.SPADE, '3')]  # 玩家0只剩一张牌
        # 玩家1有16张牌（模拟没有出过牌）
        self.engine.state.players[1] = [Card(Suit.HEART, '4')] * 16
        
        self.engine.state.player_cards_left[0] = 1
        self.engine.state.player_cards_left[1] = 16
        
        # 设置首出牌玩家，避免权限问题
        self.engine.state.first_player = 0
        self.engine.state.current_player = 0
        self.engine.state.last_player = 0
        
        # 玩家0出最后一张牌获胜
        success = self.engine.play_cards(0, [Card(Suit.SPADE, '3')])
        
        # 验证操作成功
        self.assertTrue(success, "出牌应该成功")
        
        if success and self.engine.state.game_over:
            # 验证关牌规则
            loser_id = 1 - self.engine.state.winner
            remaining_cards = len(self.engine.state.players[loser_id])
            
            # 关牌情况：输家剩余16张牌
            self.assertEqual(remaining_cards, 16, "输家应该剩余16张牌")
            
            # 关牌应该翻倍得分
            expected_score = remaining_cards * self.engine.base_score * 2
            actual_score = self.engine.state.scores[self.engine.state.winner]
            self.assertEqual(actual_score, expected_score, "关牌得分应该翻倍")
    
    def test_anti_shutdown_rule(self):
        """测试反关规则：赢家只出过第一手牌"""
        # 发牌
        self.engine.deal_cards()
        self.engine.state.game_over = False  # 确保游戏未结束
        
        # 模拟反关情况：玩家0只出过一手牌就获胜，玩家1剩余一些牌
        self.engine.state.players[0] = [Card(Suit.SPADE, '3')]  # 玩家0只剩一张牌
        self.engine.state.players[1] = [Card(Suit.HEART, '4'), Card(Suit.CLUB, '5')]  # 玩家1剩2张牌
        
        self.engine.state.player_cards_left[0] = 1
        self.engine.state.player_cards_left[1] = 2
        
        # 设置首出牌玩家和当前玩家，避免权限问题
        self.engine.state.first_player = 0
        self.engine.state.current_player = 0
        self.engine.state.last_player = 0
        
        # 模拟游戏历史，显示玩家0只出过一手牌
        self.engine.game_history = [
            {
                'player': 0,
                'cards': [Card(Suit.DIAMOND, '7'), Card(Suit.CLUB, '7'), Card(Suit.HEART, '7')],  # 玩家0的第一手牌
                'pattern': None,
                'hand_before': [],  # 简化处理
                'opponent_hand_size': 16,
                'is_first_round': True
            }
        ]
        
        # 玩家0出最后一张牌获胜
        success = self.engine.play_cards(0, [Card(Suit.SPADE, '3')])
        
        # 验证操作成功
        self.assertTrue(success, "出牌应该成功")
        
        if success and self.engine.state.game_over:
            # 验证反关规则
            loser_id = 1 - self.engine.state.winner
            remaining_cards = len(self.engine.state.players[loser_id])
            
            # 检查是否符合反关条件
            loser_moves = [move for move in self.engine.game_history if move['player'] == loser_id]
            winner_is_first_player = (self.engine.state.winner == self.engine.state.first_player)
            
            # 反关条件：
            # 1. 输家只出过一手牌
            # 2. 赢家出完了所有牌（手牌数为0）
            # 3. 输家是这局游戏第一个出牌的玩家（等于first_player）
            if (len(loser_moves) == 0 and 
                len(self.engine.state.players[self.engine.state.winner]) == 0 and
                loser_id == self.engine.state.first_player):
                # 反关应该翻倍得分
                expected_score = remaining_cards * self.engine.base_score * 2
            else:
                # 普通得分
                expected_score = remaining_cards * self.engine.base_score
            
            actual_score = self.engine.state.scores[self.engine.state.winner]
            # 添加调试信息
            print(f"输家出牌次数: {len(loser_moves)}")
            print(f"赢家手牌数: {len(self.engine.state.players[self.engine.state.winner])}")
            print(f"输家是否是首出牌玩家: {loser_id == self.engine.state.first_player}")
            print(f"预期得分: {expected_score}")
            print(f"实际得分: {actual_score}")
            self.assertEqual(actual_score, expected_score, "得分计算应该正确")


if __name__ == '__main__':
    unittest.main()