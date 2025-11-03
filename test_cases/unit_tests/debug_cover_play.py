from game import GameEngine
from cards import Card, Suit, CardPattern, CardType, compare_patterns

# 创建测试用例来重现问题
def test_cover_play_issue():
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
    print("is_cover_play:", engine.is_cover_play())
    
    # 测试首出情况
    engine.state.last_pattern = None
    print("首出情况 is_cover_play:", engine.is_cover_play())
    groups = engine.get_valid_pattern_groups(0)
    print(f"首出情况分组数量: {len(groups)}")
    
    # 测试被单张4压制的情况
    engine.state.last_pattern = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '4')], 4)
    engine.state.pass_count = 0
    print("被单张4压制 is_cover_play:", engine.is_cover_play())
    
    # 手动检查所有分组
    all_patterns = []
    engine._generate_all_patterns(engine.state.players[0], all_patterns)
    all_groups = engine.group_patterns_into_hands(engine.state.players[0], all_patterns)
    
    print(f"所有分组数量: {len(all_groups)}")
    
    # 检查每个分组是否包含能管住4的牌型
    valid_groups = []
    for i, group in enumerate(all_groups):
        can_beat = any(compare_patterns(pattern, engine.state.last_pattern) for pattern in group)
        if can_beat:
            valid_groups.append(group)
    
    print(f"能管住4的分组数量: {len(valid_groups)}")
    
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
    test_cover_play_issue()