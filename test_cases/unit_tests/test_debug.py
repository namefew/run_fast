"""
测试修复后的跳过逻辑
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from game import GameEngine
from cards import Card, Suit
from human_strategy import HumanStrategy

def test_skip_logic():
    """测试跳过逻辑"""
    print("=== 测试跳过逻辑 ===")
    
    # 创建游戏引擎
    engine = GameEngine()
    
    # 设置特定的手牌用于测试
    engine.state.players[0] = [
        Card(Suit.SPADE, '3'),
        Card(Suit.SPADE, '4'),
        Card(Suit.SPADE, '5')
    ]
    
    engine.state.players[1] = [
        Card(Suit.HEART, '7'),
        Card(Suit.HEART, '8'),
        Card(Suit.HEART, '9')
    ]
    
    engine.state.current_player = 0
    engine.state.first_player = 0
    
    # 玩家0出一个单牌
    result = engine.play_cards(0, [Card(Suit.SPADE, '3')])
    print(f"玩家0出牌结果: {result}")
    print(f"玩家0出牌后，游戏历史记录数量: {len(engine.game_history)}")
    
    # 设置上一手牌，这样玩家1就可以跳过了
    from cards import CardPattern, CardType
    engine.state.last_pattern = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, '2')], 15)  # 2比3小
    
    # 玩家1跳过
    result = engine.pass_turn(1)
    print(f"玩家1跳过结果: {result}")
    print(f"玩家1跳过后，游戏历史记录数量: {len(engine.game_history)}")
    
    # 检查游戏历史
    for i, move in enumerate(engine.game_history):
        print(f"历史记录 {i}: 玩家{move['player']}, 牌数={len(move['cards'])}, pattern={move['pattern']}")
    
    # 测试HumanStrategy的refine_remaining_cards方法
    strategy = HumanStrategy(0)
    refined_cards = strategy.refine_remaining_cards(engine)
    print(f"精炼后的剩余牌数: {len(refined_cards)}")
    
    # 查看跳过的记录
    if len(engine.game_history) >= 2:
        skip_move = engine.game_history[1]
        print(f"跳过记录: {skip_move}")

if __name__ == "__main__":
    test_skip_logic()