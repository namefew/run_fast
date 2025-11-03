from game import GameEngine
from cards import Card, Suit, CardPattern, CardType

def simple_test():
    engine = GameEngine()
    # 设置简单的测试手牌
    engine.state.players[0] = [
        Card(Suit.SPADE, '3'),
        Card(Suit.HEART, '4'),
        Card(Suit.SPADE, '5')
    ]
    
    print("手牌:", [str(card) for card in engine.state.players[0]])
    
    # 测试首出情况
    engine.state.last_pattern = None
    groups = engine.get_valid_pattern_groups(0)
    print(f"首出情况分组数量: {len(groups)}")
    
    # 测试被单张4压制的情况
    engine.state.last_pattern = CardPattern(CardType.SINGLE, [Card(Suit.HEART, '4')], 4)
    engine.state.pass_count = 0
    
    groups = engine.get_valid_pattern_groups(0)
    print(f"被单张4压制分组数量: {len(groups)}")
    
    if groups:
        for i, group in enumerate(groups):
            print(f"分组 {i+1}:")
            for pattern in group:
                print(f"  {pattern}")

if __name__ == "__main__":
    simple_test()