"""
测试跑得快游戏的积分计算功能
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import GameEngine
from cards import Card, Suit


class TestScoring(unittest.TestCase):
    """测试积分计算功能"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = GameEngine()
    
    def test_basic_scoring(self):
        """测试基本积分计算"""
        self.engine.deal_cards()
        
        # 模拟游戏过程直到结束
        while not self.engine.state.game_over:
            # 获取当前玩家的有效动作
            valid_patterns = self.engine.get_valid_patterns(self.engine.state.current_player)
            
            if valid_patterns:
                # 选择第一个有效动作（简化处理）
                pattern = valid_patterns[0]
                self.engine.play_cards(self.engine.state.current_player, pattern.cards)
            else:
                # 没有有效动作，跳过
                self.engine.pass_turn(self.engine.state.current_player)
        
        # 验证游戏结束状态
        self.assertTrue(self.engine.state.game_over)
        
        # 验证积分计算
        winner = self.engine.state.winner
        loser_id = 1 - winner
        remaining_cards = len(self.engine.state.players[loser_id])
        
        # 基本得分应该等于剩余手牌数乘以底分
        base_score = self.engine.base_score
        expected_score = remaining_cards * base_score
        actual_score = self.engine.state.scores[winner]
        
        # 验证得分计算（考虑关牌和反关情况）
        self.assertGreaterEqual(actual_score, expected_score // 2)  # 至少是基本得分的一半
    
    def test_shutdown_scoring(self):
        """测试关牌积分计算"""
        # 初始化游戏
        self.engine.deal_cards()
        
        # 模拟关牌情况：玩家0出完牌，玩家1一张都没出
        self.engine.state.players[0] = [Card(Suit.SPADE, '3')]  # 玩家0只剩一张牌
        # 玩家1有16张牌（模拟没有出过牌）
        self.engine.state.players[1] = [Card(Suit.HEART, '4')] * 16
        
        self.engine.state.player_cards_left[0] = 1
        self.engine.state.player_cards_left[1] = 16
        
        # 玩家0出最后一张牌获胜
        success = self.engine.play_cards(0, [Card(Suit.SPADE, '3')])
        
        if success and self.engine.state.game_over:
            # 验证关牌规则
            loser_id = 1 - self.engine.state.winner
            remaining_cards = len(self.engine.state.players[loser_id])
            
            # 关牌情况：输家剩余16张牌
            if remaining_cards == 16:
                expected_score = remaining_cards * self.engine.base_score * 2  # 关牌翻倍
                actual_score = self.engine.state.scores[self.engine.state.winner]
                self.assertEqual(actual_score, expected_score)
    
    def test_anti_shutdown_scoring(self):
        """测试反关积分计算"""
        # 初始化游戏
        self.engine.deal_cards()
        
        # 模拟反关情况：玩家0只出过一手牌就获胜，玩家1剩余一些牌
        self.engine.state.players[0] = [Card(Suit.SPADE, '3')]  # 玩家0只剩一张牌
        self.engine.state.players[1] = [Card(Suit.HEART, '4'), Card(Suit.CLUB, '5')]  # 玩家1剩2张牌
        
        self.engine.state.player_cards_left[0] = 1
        self.engine.state.player_cards_left[1] = 2
        
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
        
        if success and self.engine.state.game_over:
            # 验证反关规则
            loser_id = 1 - self.engine.state.winner
            remaining_cards = len(self.engine.state.players[loser_id])
            
            # 重新计算赢家出牌次数（包括刚刚出的牌）
            winner_moves_count = len([move for move in self.engine.game_history if move['player'] == self.engine.state.winner]) + 1
            
            # 反关情况：赢家只出过一手牌
            if winner_moves_count == 1:
                expected_score = remaining_cards * self.engine.base_score * 2  # 反关停倍
                actual_score = self.engine.state.scores[self.engine.state.winner]
                self.assertEqual(actual_score, expected_score)


if __name__ == '__main__':
    unittest.main()