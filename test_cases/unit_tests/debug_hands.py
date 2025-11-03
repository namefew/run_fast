"""
调试手牌分组问题
"""

from game import GameEngine
from cards import Card, Suit, CardPattern, CardType

def test_problematic_hand():
    """测试有问题的手牌"""
    # 创建游戏引擎
    engine = GameEngine()
    
    # 手动设置手牌: [3, 3, 4, 4, 4, 5, 6, 6, 7, 7, 8, 9, J, K, K, K]
    hand = [
        Card(Suit.SPADE, '3'),
        Card(Suit.HEART, '3'),
        Card(Suit.SPADE, '4'),
        Card(Suit.HEART, '4'),
        Card(Suit.DIAMOND, '4'),
        Card(Suit.SPADE, '5'),
        Card(Suit.HEART, '6'),
        Card(Suit.DIAMOND, '6'),
        Card(Suit.SPADE, '7'),
        Card(Suit.HEART, '7'),
        Card(Suit.SPADE, '8'),
        Card(Suit.SPADE, '9'),
        Card(Suit.SPADE, 'J'),
        Card(Suit.SPADE, 'K'),
        Card(Suit.HEART, 'K'),
        Card(Suit.DIAMOND, 'K')
    ]
    
    engine.state.players[0] = hand
    engine.state.players[1] = []  # 对手空手牌
    
    print("手牌:")
    for card in hand:
        print(card, end=" ")
    print("\n")
    
    # 测试首出牌情况
    print("=== 首出牌情况 ===")
    engine.state.last_pattern = None  # 首出牌
    valid_groups = engine.get_valid_pattern_groups(0)
    
    print(f"有效分组数量: {len(valid_groups)}")
    
    if valid_groups:
        print("前5个有效分组:")
        for i, group in enumerate(valid_groups[:5]):
            print(f"分组 {i+1}:")
            for j, pattern in enumerate(group):
                print(f"  {j+1}. {pattern}")
            print()
    
    # 测试跟牌情况 - 被单张4压制
    print("=== 跟牌情况（被单张4压制） ===")
    engine.state.last_pattern = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '4')], 4)
    valid_groups = engine.get_valid_pattern_groups(0)
    
    print(f"有效分组数量: {len(valid_groups)}")
    
    if valid_groups:
        print("前5个有效分组:")
        for i, group in enumerate(valid_groups[:5]):
            print(f"分组 {i+1}:")
            for j, pattern in enumerate(group):
                print(f"  {j+1}. {pattern}")
            print()
    else:
        print("没有找到有效的分组！")

if __name__ == "__main__":
    test_problematic_hand()