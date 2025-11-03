"""
测试HumanStrategy中的跳过逻辑处理
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from game import GameEngine
from cards import Card, Suit, CardPattern, CardType
from human_strategy import HumanStrategy

def test_human_strategy_skip_detection():
    """测试HumanStrategy是否能正确检测跳过"""
    print("=== 测试HumanStrategy跳过检测 ===")
    
    # 创建游戏引擎
    engine = GameEngine()
    
    # 设置特定的手牌用于测试
    engine.state.players[0] = [
        Card(Suit.SPADE, 'K'),
        Card(Suit.SPADE, 'A'),
        Card(Suit.SPADE, '2')
    ]
    
    engine.state.players[1] = [
        Card(Suit.HEART, '7'),
        Card(Suit.HEART, '8'),
        Card(Suit.HEART, '9')
    ]
    
    engine.state.current_player = 0
    engine.state.first_player = 0
    
    # 玩家0出一个单牌 K
    engine.play_cards(0, [Card(Suit.SPADE, 'K')])
    print(f"玩家0出牌后，游戏历史记录数量: {len(engine.game_history)}")
    
    # 设置上一手牌为A，这样玩家1就可以跳过了（因为7,8,9都小于A）
    engine.state.last_pattern = CardPattern(CardType.SINGLE, [Card(Suit.SPADE, 'A')], 14)
    
    # 玩家1跳过
    engine.pass_turn(1)
    print(f"玩家1跳过后，游戏历史记录数量: {len(engine.game_history)}")
    
    # 检查游戏历史
    print("游戏历史记录:")
    for i, move in enumerate(engine.game_history):
        print(f"  {i}: 玩家{move['player']}, 牌数={len(move['cards'])}, pattern={move['pattern']}")
    
    # 测试HumanStrategy的refine_remaining_cards方法
    strategy = HumanStrategy(0)
    print("\n调用refine_remaining_cards方法:")
    refined_cards = strategy.refine_remaining_cards(engine)
    print(f"精炼后的剩余牌数: {len(refined_cards)}")
    
    # 检查是否检测到跳过
    print("\n检查跳过检测逻辑:")
    skipped_moves = []
    opponent_id = 1
    for i in range(len(engine.game_history) - 1):
        move = engine.game_history[i]
        next_move = engine.game_history[i + 1] if i + 1 < len(engine.game_history) else None
        # 如果当前玩家出牌，下一个玩家跳过，说明下一个玩家无法管住当前玩家的牌
        if move['player'] != opponent_id and next_move and next_move['player'] == opponent_id and not next_move['cards']:
            skipped_moves.append(move)
            print(f"  检测到跳过: 玩家{move['player']}出牌{move['pattern']}，玩家{next_move['player']}跳过")
    
    print(f"总共检测到 {len(skipped_moves)} 次跳过")

if __name__ == "__main__":
    test_human_strategy_skip_detection()