"""
测试三带二牌型识别
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cards import Card, Suit, detect_card_type, CardType


class TestThreeWithTwo(unittest.TestCase):
    """测试三带二牌型识别"""
    
    def test_three_with_two_valid(self):
        """测试有效的三带二牌型识别"""
        # 测试用例1: 三张相同 + 一对
        cards1 = [
            Card(Suit.SPADE, '7'),
            Card(Suit.HEART, '7'),
            Card(Suit.CLUB, '7'),
            Card(Suit.DIAMOND, '9'),
            Card(Suit.SPADE, '9')
        ]
        
        pattern1 = detect_card_type(cards1)
        self.assertIsNotNone(pattern1)
        if pattern1:
            self.assertEqual(pattern1.type, CardType.THREE_WITH_TWO)
    
    def test_three_with_two_single_cards(self):
        """测试三张相同 + 两张不同的单牌"""
        # 测试用例2: 三张相同 + 两张不同的单牌
        cards2 = [
            Card(Suit.SPADE, '7'),
            Card(Suit.HEART, '7'),
            Card(Suit.CLUB, '7'),
            Card(Suit.DIAMOND, '9'),
            Card(Suit.SPADE, '10')
        ]
        
        pattern2 = detect_card_type(cards2)
        self.assertIsNotNone(pattern2)
        if pattern2:
            self.assertEqual(pattern2.type, CardType.THREE_WITH_TWO)
    
    def test_not_three_with_two_pairs(self):
        """测试两对（不是三带二）"""
        # 测试用例3: 两对（不是三带二）
        cards3 = [
            Card(Suit.SPADE, '7'),
            Card(Suit.HEART, '7'),
            Card(Suit.CLUB, '9'),
            Card(Suit.DIAMOND, '9'),
            Card(Suit.SPADE, '10')
        ]
        
        pattern3 = detect_card_type(cards3)
        # 这不应该被识别为三带二
        if pattern3:
            self.assertNotEqual(pattern3.type, CardType.THREE_WITH_TWO)
    
    def test_not_three_with_two_four_same(self):
        """测试四张相同（不是三带二）"""
        # 测试用例4: 四张相同（不是三带二）
        cards4 = [
            Card(Suit.SPADE, '7'),
            Card(Suit.HEART, '7'),
            Card(Suit.CLUB, '7'),
            Card(Suit.DIAMOND, '7'),
            Card(Suit.SPADE, '10')
        ]
        
        pattern4 = detect_card_type(cards4)
        # 这不应该被识别为三带二
        if pattern4:
            self.assertNotEqual(pattern4.type, CardType.THREE_WITH_TWO)


if __name__ == "__main__":
    unittest.main()