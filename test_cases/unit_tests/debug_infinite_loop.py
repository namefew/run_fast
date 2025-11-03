"""
调试手牌分组时的无限循环问题
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from game import GameEngine
from cards import Card, Suit, CardPattern, CardType

def test_problematic_hand():
    """测试有问题的手牌"""
    # 创建游戏引擎
    engine = GameEngine()
    
    # 设置有问题的手牌: [3, 3, 3, 4, 10, 10, 10, J, J, J, Q, Q, K, A]
    hand = [
        Card(Suit.SPADE, '3'),
        Card(Suit.HEART, '3'),
        Card(Suit.CLUB, '3'),
        Card(Suit.SPADE, '4'),
        Card(Suit.HEART, '10'),
        Card(Suit.CLUB, '10'),
        Card(Suit.SPADE, '10'),
        Card(Suit.HEART, 'J'),
        Card(Suit.CLUB, 'J'),
        Card(Suit.SPADE, 'J'),
        Card(Suit.HEART, 'Q'),
        Card(Suit.CLUB, 'Q'),
        Card(Suit.SPADE, 'K'),
        Card(Suit.SPADE, 'A')
    ]
    
    # 设置玩家手牌
    engine.state.players[0] = hand
    engine.state.players[1] = []  # 对手没有牌
    
    print("测试手牌:")
    for card in hand:
        print(f"  {card}")
    print()
    
    # 先测试非压牌状态
    print("测试非压牌状态:")
    try:
        pattern_groups = engine.get_valid_pattern_groups(0)
        print(f"成功获取到 {len(pattern_groups)} 个分组")
        
        # 显示前几个分组作为示例
        for i, group in enumerate(pattern_groups[:3]):
            print(f"分组 {i+1}:")
            for pattern in group:
                print(f"  {pattern}")
            print()
    except Exception as e:
        print(f"出现异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 再测试压牌状态
    print("\n测试压牌状态:")
    # 设置上一手牌为一个较小的牌型，例如单张5
    engine.state.last_pattern = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '5')], 5)
    try:
        pattern_groups = engine.get_valid_pattern_groups(0)
        print(f"成功获取到 {len(pattern_groups)} 个分组")
        
        # 显示前几个分组作为示例
        for i, group in enumerate(pattern_groups[:3]):
            print(f"分组 {i+1}:")
            for pattern in group:
                print(f"  {pattern}")
            print()
    except Exception as e:
        print(f"出现异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_problematic_hand()