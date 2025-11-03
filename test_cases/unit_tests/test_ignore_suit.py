"""
测试忽略花色的牌型生成和分组
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from game import GameEngine
from cards import Card, Suit

def test_ignore_suit():
    """测试忽略花色的牌型生成和分组"""
    engine = GameEngine()
    
    # 测试手牌: [3♠, 3♥, 4♠, 4♥, 5♠, 5♥, 6♠, 6♥]
    # 在考虑花色的情况下，这应该可以组成连对
    # 在忽略花色的情况下，这也应该可以组成连对
    hand = [
        Card(Suit.SPADE, '3'),
        Card(Suit.HEART, '3'),
        Card(Suit.SPADE, '4'),
        Card(Suit.HEART, '4'),
        Card(Suit.SPADE, '5'),
        Card(Suit.HEART, '5'),
        Card(Suit.SPADE, '6'),
        Card(Suit.HEART, '6')
    ]
    
    engine.state.players[0] = hand
    
    print("测试手牌:")
    for card in hand:
        print(f"  {card}", end=" ")
    print("\n")
    
    # 生成所有可能的牌型
    all_patterns = []
    engine._generate_all_patterns(hand, all_patterns)
    print(f"生成的牌型数量: {len(all_patterns)}")
    
    # 显示一些生成的牌型
    print("部分生成的牌型:")
    for i, pattern in enumerate(all_patterns[:10]):
        print(f"  {i+1}. {pattern}")
    print()
    
    # 测试分组
    groups = engine.group_patterns_into_hands(hand, all_patterns)
    print(f"分组数量: {len(groups)}")
    
    if groups:
        print("前3个分组:")
        for i, group in enumerate(groups[:3]):
            print(f"  分组 {i+1}:")
            for j, pattern in enumerate(group):
                print(f"    {j+1}. {pattern}")
            print()
    else:
        print("无法分组")

def test_problematic_hand():
    """测试之前有问题的手牌"""
    engine = GameEngine()
    
    # 之前有问题的手牌: [3, 4, 7, 9, J, J, Q, Q, K, K, A, A]
    hand = [
        Card(Suit.SPADE, '3'),
        Card(Suit.HEART, '4'),
        Card(Suit.SPADE, '7'),
        Card(Suit.SPADE, '9'),
        Card(Suit.SPADE, 'J'),
        Card(Suit.HEART, 'J'),
        Card(Suit.SPADE, 'Q'),
        Card(Suit.HEART, 'Q'),
        Card(Suit.SPADE, 'K'),
        Card(Suit.HEART, 'K'),
        Card(Suit.SPADE, 'A'),
        Card(Suit.HEART, 'A')
    ]
    
    engine.state.players[0] = hand
    
    print("测试有问题的手牌:")
    for card in hand:
        print(f"  {card}", end=" ")
    print("\n")
    
    # 生成所有可能的牌型
    all_patterns = []
    engine._generate_all_patterns(hand, all_patterns)
    print(f"生成的牌型数量: {len(all_patterns)}")
    
    # 测试分组
    groups = engine.group_patterns_into_hands(hand, all_patterns)
    print(f"分组数量: {len(groups)}")
    
    if groups:
        print("前3个分组:")
        for i, group in enumerate(groups[:3]):
            print(f"  分组 {i+1}:")
            for j, pattern in enumerate(group):
                print(f"    {j+1}. {pattern}")
            print()
    else:
        print("无法分组")

if __name__ == "__main__":
    print("=== 测试忽略花色的牌型生成和分组 ===")
    test_ignore_suit()
    
    print("\n=== 测试之前有问题的手牌 ===")
    test_problematic_hand()