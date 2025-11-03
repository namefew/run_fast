"""
测试牌型生成和分组时忽略花色的特性
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from game import GameEngine
from cards import Card, Suit, CardType

def test_suit_independence():
    """测试牌型生成和分组时忽略花色"""
    engine = GameEngine()
    
    # 测试用例1: 创建两组牌，点数相同但花色不同
    hand1 = [
        Card(Suit.SPADE, '3'),
        Card(Suit.SPADE, '4'),
        Card(Suit.SPADE, '5'),
        Card(Suit.SPADE, '6'),
        Card(Suit.SPADE, '7')
    ]
    
    hand2 = [
        Card(Suit.HEART, '3'),
        Card(Suit.DIAMOND, '4'),
        Card(Suit.CLUB, '5'),
        Card(Suit.SPADE, '6'),
        Card(Suit.HEART, '7')
    ]
    
    # 生成两组牌的牌型
    patterns1 = []
    patterns2 = []
    engine._generate_all_patterns(hand1, patterns1)
    engine._generate_all_patterns(hand2, patterns2)
    
    # 检查是否都能生成顺子
    straight1 = any(p.type == CardType.STRAIGHT for p in patterns1)
    straight2 = any(p.type == CardType.STRAIGHT for p in patterns2)
    
    print("测试用例1: 忽略花色生成顺子")
    print(f"  同花色顺子(♠3-7): {'能生成' if straight1 else '不能生成'}")
    print(f"  混合花色顺子(3-7): {'能生成' if straight2 else '不能生成'}")
    print(f"  结果: {'通过' if straight1 and straight2 else '失败'}")
    print()
    
    # 测试用例2: 检查分组时忽略花色
    hand3 = [
        Card(Suit.SPADE, '8'),
        Card(Suit.HEART, '8'),
        Card(Suit.DIAMOND, '8'),
        Card(Suit.SPADE, '9'),
        Card(Suit.HEART, '9'),
        Card(Suit.DIAMOND, '9')
    ]
    
    engine.state.players[0] = hand3
    all_patterns = []
    engine._generate_all_patterns(hand3, all_patterns)
    groups = engine.group_patterns_into_hands(hand3, all_patterns)
    
    print("测试用例2: 忽略花色进行分组")
    print(f"  手牌: {[str(card) for card in hand3]}")
    print(f"  生成牌型数量: {len(all_patterns)}")
    print(f"  分组数量: {len(groups)}")
    
    # 检查是否能生成飞机
    has_airplane = any(
        any(pattern.type == CardType.AIRPLANE for pattern in group) 
        for group in groups
    )
    print(f"  能否生成飞机: {'能' if has_airplane else '不能'}")
    print(f"  结果: {'通过' if has_airplane else '失败'}")
    print()
    
    # 测试用例3: 原始问题手牌
    print("测试用例3: 原始问题手牌")
    problematic_hand = [
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
    
    engine.state.players[0] = problematic_hand
    all_patterns = []
    engine._generate_all_patterns(problematic_hand, all_patterns)
    groups = engine.group_patterns_into_hands(problematic_hand, all_patterns)
    
    print(f"  手牌: {[str(card) for card in problematic_hand]}")
    print(f"  生成牌型数量: {len(all_patterns)}")
    print(f"  分组数量: {len(groups)}")
    
    # 检查是否能分组
    can_group = len(groups) > 0
    print(f"  能否成功分组: {'能' if can_group else '不能'}")
    print(f"  结果: {'通过' if can_group else '失败'}")
    
    if groups:
        print("  前3个分组示例:")
        for i, group in enumerate(groups[:3]):
            print(f"    分组 {i+1}: {[str(pattern) for pattern in group]}")

if __name__ == "__main__":
    test_suit_independence()