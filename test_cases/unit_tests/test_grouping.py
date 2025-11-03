from game import GameEngine
from cards import Card, Suit

# 创建测试用例
def test_grouping_issue():
    engine = GameEngine()
    engine.state.players[0] = [
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
    
    print("手牌:", [str(card) for card in engine.state.players[0]])
    
    # 获取所有可能的牌型组合
    all_patterns = []
    engine.generate_all_patterns(engine.state.players[0], all_patterns)
    print(f"生成的牌型数量: {len(all_patterns)}")
    
    # 尝试分组
    groups = engine.group_patterns_into_hands(engine.state.players[0], all_patterns)
    print(f"分组数量: {len(groups)}")
    
    if groups:
        for i, group in enumerate(groups[:5]):  # 只显示前5组
            print(f"分组 {i+1}:")
            for pattern in group:
                print(f"  {pattern}")
    else:
        print("无法分组")

if __name__ == "__main__":
    test_grouping_issue()