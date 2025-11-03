from game import GameEngine
from cards import Card, Suit, CardPattern, CardType, compare_patterns

# 创建测试用例来重现问题
def test_detailed_issue():
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
    
    # 测试生成所有牌型
    all_patterns = []
    engine.generate_all_patterns(engine.state.players[0], all_patterns)
    print(f"生成的牌型数量: {len(all_patterns)}")
    
    # 测试分组
    groups = engine.group_patterns_into_hands(engine.state.players[0], all_patterns)
    print(f"\n分组数量: {len(groups)}")
    
    # 测试被单张4压制的情况
    engine.state.last_pattern = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '4')], 4)
    engine.state.pass_count = 0
    print(f"\n被单张4压制 is_cover_play: {engine.is_cover_play()}")
    
    # 检查哪些牌型能管住4
    can_beat_patterns = [p for p in all_patterns if compare_patterns(p, engine.state.last_pattern)]
    print(f"能管住4的牌型数量: {len(can_beat_patterns)}")
    
    groups = engine.get_valid_pattern_groups(0)
    print(f"被单张4压制分组数量: {len(groups)}")
    
    if groups:
        for i, group in enumerate(groups[:3]):  # 只显示前3组
            print(f"分组 {i+1}:")
            for pattern in group:
                print(f"  {pattern}")
    else:
        print("无法分组")

if __name__ == "__main__":
    test_detailed_issue()