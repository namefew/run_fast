"""
分析手牌分组情况的脚本
"""

from game import GameEngine
from cards import Card, Suit
from human_strategy import HumanStrategy

def create_hand_from_string(hand_str):
    """从字符串创建手牌"""
    # 解析手牌字符串
    ranks = hand_str.split(', ')
    hand = []
    
    # 用于跟踪每种牌的花色
    suit_counters = {}
    
    for rank in ranks:
        # 确定花色
        if rank not in suit_counters:
            suit_counters[rank] = 0
        else:
            suit_counters[rank] += 1
            
        # 根据计数选择花色
        suit_index = suit_counters[rank] % 4
        suit = list(Suit)[suit_index]
        
        # 创建牌
        card = Card(suit, rank)
        hand.append(card)
    
    return hand

def analyze_hand_grouping(hand_str):
    """分析手牌分组情况"""
    print(f"分析手牌: [{hand_str}]")
    
    # 创建手牌
    hand = create_hand_from_string(hand_str)
    print("手牌详情:")
    for card in hand:
        print(f"  {card}")
    
    # 创建游戏引擎和策略
    engine = GameEngine()
    engine.state.current_player = 0
    engine.state.players[0] = hand
    engine._update_remaining_cards()
    strategy = HumanStrategy(player_id=0)

    # 生成所有可能的牌型
    all_patterns = []
    engine._generate_all_patterns(hand, all_patterns)
    print(f"\n生成的牌型数量: {len(all_patterns)}")
    
    # 生成分组
    pattern_groups = engine.group_patterns_into_hands(hand, all_patterns)
    print(f"生成的分组数量: {len(pattern_groups)}")
    
    # 显示前几个分组
    print("\n前5个分组:")
    for i, group in enumerate(pattern_groups[:5]):
        print(f"  分组 {i+1}:")
        total_cards = 0
        for j, pattern in enumerate(group):
            print(f"    {j+1}. {pattern}")
            total_cards += pattern.card_count
        print(f"    总牌数: {total_cards} ")
    
    # 使用HumanStrategy评估手牌
    print("\n使用HumanStrategy评估:")
    remaining_cards = strategy.refine_remaining_cards(engine)
    opponent_patterns = strategy.generate_all_patterns_from_cards(remaining_cards,engine)
    remaining_score = strategy._evaluate_remaining_hand(hand, opponent_patterns, engine)
    print(f"  剩余手牌评估得分: {remaining_score}")
    
    # 使用HumanStrategy的calculate_group_score方法评估各个分组
    print("\n分组评分:")
    for i, group in enumerate(pattern_groups[:5]):  # 只评估前5个分组
        try:
            # 创建一个临时的对手手牌，假设对手有16张牌
            engine.state.players[1] = [Card(Suit.SPADE, '3')] * 16  # 占位符
            score = strategy.calculate_group_score(group, opponent_patterns, engine)
            print(f"  分组 {i+1} 得分: {score}")
        except Exception as e:
            print(f"  分组 {i+1} 评分失败: {e}")

if __name__ == "__main__":
    # 分析指定的手牌
    hand_str = "3, 3, 4, 5, 7, 8, 8, 9, 9, Q, Q, Q, K, K, K, 2"
    analyze_hand_grouping(hand_str)