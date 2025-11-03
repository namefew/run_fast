"""
测试牌类和牌型处理
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from cards import Card, Suit, create_deck, detect_card_type, CardType, CardPattern


class TestCards(unittest.TestCase):
    
    def test_card_creation(self):
        """测试牌的创建"""
        card = Card(Suit.SPADE, '3')
        self.assertEqual(card.suit, Suit.SPADE)
        self.assertEqual(card.rank, '3')
        self.assertEqual(card.point, 3)
    
    def test_card_comparison(self):
        """测试牌的比较"""
        card3 = Card(Suit.SPADE, '3')
        card2 = Card(Suit.SPADE, '2')
        
        # 2比3大
        self.assertTrue(card3 < card2)
        
        cardA = Card(Suit.SPADE, 'A')
        self.assertTrue(cardA < card2)  # A比2小
        self.assertTrue(card3 < cardA)  # 3比A大（A在这里作为1使用）
    
    def test_create_deck(self):
        """测试创建牌堆"""
        deck = create_deck()
        self.assertEqual(len(deck), 48)  # 应该有48张牌
        
        # 检查是否有黑桃2但没有其他2
        spade_2_count = sum(1 for card in deck if card.suit == Suit.SPADE and card.rank == '2')
        other_2_count = sum(1 for card in deck if card.suit != Suit.SPADE and card.rank == '2')
        
        self.assertEqual(spade_2_count, 1)
        self.assertEqual(other_2_count, 0)
        
        # 检查没有黑桃A
        spade_A_count = sum(1 for card in deck if card.suit == Suit.SPADE and card.rank == 'A')
        self.assertEqual(spade_A_count, 0)
    
    def test_detect_single(self):
        """测试单张识别"""
        cards = [Card(Suit.SPADE, '3')]
        pattern = detect_card_type(cards)
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.type, CardType.SINGLE)
        self.assertEqual(pattern.main_point, 3)
    
    def test_detect_pair(self):
        """测试对子识别"""
        cards = [Card(Suit.SPADE, '3'), Card(Suit.HEART, '3')]
        pattern = detect_card_type(cards)
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.type, CardType.PAIR)
        self.assertEqual(pattern.main_point, 3)
    
    def test_detect_invalid_pair(self):
        """测试无效对子识别"""
        cards = [Card(Suit.SPADE, '3'), Card(Suit.HEART, '4')]
        pattern = detect_card_type(cards)
        self.assertIsNone(pattern)
    
    def test_detect_bomb_four_same(self):
        """测试四张相同炸弹识别"""
        cards = [Card(Suit.SPADE, '3'), Card(Suit.HEART, '3'), 
                Card(Suit.DIAMOND, '3'), Card(Suit.CLUB, '3')]
        pattern = detect_card_type(cards)
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.type, CardType.BOMB)
        self.assertEqual(pattern.main_point, 3)
    
    def test_detect_bomb_three_aces(self):
        """测试三张A炸弹识别"""
        cards = [Card(Suit.SPADE, 'A'), Card(Suit.HEART, 'A'), Card(Suit.DIAMOND, 'A')]
        pattern = detect_card_type(cards)
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.type, CardType.BOMB)
        self.assertEqual(pattern.main_point, 14)

if __name__ == '__main__':
    unittest.main()