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
    for pattern in can_beat_patterns:
        print(f"  {pattern}")
    
    # 手动调用get_valid_pattern_groups中的逻辑
    player_hand = engine.state.players[0]
    all_patterns = []
    engine.generate_all_patterns(player_hand, all_patterns)
    pattern_groups = engine.group_patterns_into_hands(player_hand, all_patterns)
    print(f"\n初始分组数量: {len(pattern_groups)}")
    
    if engine.is_cover_play():
        valid_groups = []
        for group in pattern_groups:
            # 检查组中是否有能管住上一手牌的牌型
            can_beat = any(compare_patterns(pattern, engine.state.last_pattern) for pattern in group)
            print(f"分组包含能管住4的牌型: {can_beat}")
            if can_beat:
                valid_groups.append(group)
        pattern_groups = valid_groups
        print(f"过滤后分组数量: {len(pattern_groups)}")
        
        # 重新按分组的size排序，短的在前
        pattern_groups.sort(key=len)
        
        # 如果没有能管住上一手牌的完整分组，返回所有分组（允许玩家选择pass）
        if not pattern_groups:
            print("没有能管住上一手牌的完整分组，返回所有分组")
            pattern_groups = engine.group_patterns_into_hands(player_hand, all_patterns)
            pattern_groups.sort(key=len)
        else:
            print("有能管住上一手牌的完整分组")
    
    print(f"最终分组数量: {len(pattern_groups)}")

if __name__ == "__main__":
    test_detailed_issue()