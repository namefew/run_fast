"""
跑得快游戏主程序
"""

import argparse
from game import GameEngine
from player import AIPlayer
from strategy import AdvancedAIStrategy, SimpleAIStrategy
from rl_strategy import DQNAIStrategy, PPOAIStrategy, MonteCarloAIStrategy

# 创建全局策略映射
strategy_map = {
    "simple": SimpleAIStrategy,
    "advanced": AdvancedAIStrategy,
    "dqn": DQNAIStrategy,
    "ppo": PPOAIStrategy,
    "mcts": MonteCarloAIStrategy
}


def main(ai_type1="advanced", ai_type2="advanced", verbose=True):
    print("欢迎来到跑得快游戏!")
    
    # 创建游戏引擎
    engine = GameEngine()
    
    # 发牌
    engine.deal_cards()
    
    # 创建AI玩家
    strategy1_class = strategy_map.get(ai_type1, AdvancedAIStrategy)
    strategy2_class = strategy_map.get(ai_type2, AdvancedAIStrategy)
    
    player0 = AIPlayer(0, f"AI玩家0({ai_type1})", strategy1_class(0))
    player1 = AIPlayer(1, f"AI玩家1({ai_type2})", strategy2_class(1))
    
    # 设置玩家手牌
    player0.hand = engine.state.players[0][:]
    player1.hand = engine.state.players[1][:]
    
    print(f"玩家0的手牌数量: {len(player0.hand)}")
    print(f"玩家1的手牌数量: {len(player1.hand)}")
    print(f"首出牌玩家: {engine.state.first_player}")
    
    # 游戏主循环
    round_count = 0
    while not engine.state.game_over and round_count < 1000:  # 防止无限循环
        current_player = player0 if engine.state.current_player == 0 else player1
        if verbose:
            print(f"\n当前玩家: {current_player.name}")
        
        # 显示上一手牌
        if engine.state.last_pattern and verbose:
            print(f"上一手牌: {engine.state.last_pattern}")
        
        # AI选择行动
        action, cards = current_player.choose_action(engine)
        
        if action == "play":
            if verbose:
                print(f"{current_player.name} 出牌: {[str(card) for card in cards]}")
            if engine.play_cards(engine.state.current_player, cards):
                current_player.remove_cards(cards)
                if verbose:
                    print(f"出牌成功! {current_player.name} 剩余手牌: {len(current_player.hand)}张")
            else:
                if verbose:
                    print("出牌失败!")
                break
        else:
            if verbose:
                print(f"{current_player.name} 跳过")
            engine.pass_turn(engine.state.current_player)
        
        round_count += 1
        
        # 检查游戏是否结束
        if len(current_player.hand) == 0:
            engine.state.game_over = True
            engine.state.winner = engine.state.current_player
            if verbose:
                print(f"\n游戏结束! {current_player.name} 获胜!")
            break
    
    # 显示最终结果
    print("\n最终手牌:")
    print(f"玩家0剩余: {len(player0.hand)}张")
    print(f"玩家1剩余: {len(player1.hand)}张")
    print(f"游戏轮数: {round_count}")
    print(f"得分: 玩家0={engine.state.scores[0]}, 玩家1={engine.state.scores[1]}")


def play_game(ai1_type='advanced', ai2_type='advanced', verbose=True):
    """运行一局游戏"""
    # 创建游戏引擎
    engine = GameEngine()
    engine.reset()
    engine.deal_cards()
    
    # 创建玩家
    player0 = create_player(0, ai1_type)
    player1 = create_player(1, ai2_type)
    
    # 分发手牌
    player0.receive_cards(engine.state.players[0])
    player1.receive_cards(engine.state.players[1])
    
    if verbose:
        print("=== 跑得快游戏开始 ===")
        print(f"玩家0 ({ai1_type}): {[str(card) for card in player0.hand]}")
        print(f"玩家1 ({ai2_type}): {[str(card) for card in player1.hand]}")
        print(f"玩家{engine.state.first_player} 先出牌")
    
    # 游戏主循环
    round_count = 0
    while not engine.state.game_over and round_count < 1000:  # 防止无限循环
        current_player = player0 if engine.state.current_player == 0 else player1
        if verbose:
            print(f"\n当前玩家: {current_player.name}")
        
        # 显示上一手牌
        if engine.state.last_pattern and verbose:
            print(f"上一手牌: {engine.state.last_pattern}")
        
        # AI选择行动
        action, cards = current_player.choose_action(engine)
        
        if action == "play":
            if verbose:
                print(f"{current_player.name} 出牌: {[str(card) for card in cards]}")
            if engine.play_cards(engine.state.current_player, cards):
                current_player.remove_cards(cards)
                if verbose:
                    print(f"出牌成功! {current_player.name} 剩余手牌: {len(current_player.hand)}张")
            else:
                if verbose:
                    print("出牌失败!")
                break
        else:
            if verbose:
                print(f"{current_player.name} 跳过")
            engine.pass_turn(engine.state.current_player)
        
        round_count += 1
        
        # 检查游戏是否结束
        if len(current_player.hand) == 0:
            engine.state.game_over = True
            engine.state.winner = engine.state.current_player
            if verbose:
                print(f"\n游戏结束! {current_player.name} 获胜!")
            break
    
    if verbose:
        print(f"\n最终结果:")
        print(f"玩家0 ({ai1_type}) 剩余手牌: {len(player0.hand)}张")
        print(f"玩家1 ({ai2_type}) 剩余手牌: {len(player1.hand)}张")
        print(f"获胜玩家: 玩家{engine.state.winner} ({ai1_type if engine.state.winner == 0 else ai2_type})")
    
    return engine.state.winner, ai1_type if engine.state.winner == 0 else ai2_type


def run_tournament():
    """运行AI对战锦标赛"""
    ai_types = ['simple', 'advanced', 'dqn']
    results = {}
    
    # 初始化结果统计
    for ai1 in ai_types:
        results[ai1] = {}
        for ai2 in ai_types:
            results[ai1][ai2] = {"wins": 0, "losses": 0}
    
    # 进行对战（每种组合10局）
    total_games = len(ai_types) * len(ai_types) * 10
    game_count = 0
    
    print("开始AI对战锦标赛...")
    print(f"总共 {total_games} 局游戏")
    
    for ai1 in ai_types:
        for ai2 in ai_types:
            print(f"\n进行 {ai1} vs {ai2} 的对战...")
            for i in range(10):
                game_count += 1
                print(f"  游戏 {game_count}/{total_games}: ", end="")
                
                # 交替先手
                if i % 2 == 0:
                    winner, winner_type = play_game(ai1, ai2, verbose=False)
                    if winner == 0:  # ai1获胜
                        results[ai1][ai2]["wins"] += 1
                        print(f"{ai1} 获胜")
                    else:  # ai2获胜
                        results[ai1][ai2]["losses"] += 1
                        print(f"{ai2} 获胜")
                else:
                    winner, winner_type = play_game(ai2, ai1, verbose=False)
                    if winner == 0:  # ai2获胜（因为ai2是玩家0）
                        results[ai2][ai1]["wins"] += 1
                        print(f"{ai2} 获胜")
                    else:  # ai1获胜（因为ai1是玩家1）
                        results[ai2][ai1]["losses"] += 1
                        print(f"{ai1} 获胜")
    
    # 显示结果
    print("\n=== 锦标赛结果 ===")
    for ai1 in ai_types:
        print(f"\n{ai1} 对战结果:")
        for ai2 in ai_types:
            wins = results[ai1][ai2]["wins"]
            losses = results[ai1][ai2]["losses"]
            win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
            print(f"  vs {ai2}: {wins}胜{losses}负 (胜率: {win_rate:.2%})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='跑得快游戏')
    parser.add_argument('--ai1', type=str, default='advanced', 
                        choices=['simple', 'advanced', 'dqn', 'ppo', 'mcts'],
                        help='玩家1的AI类型')
    parser.add_argument('--ai2', type=str, default='advanced', 
                        choices=['simple', 'advanced', 'dqn', 'ppo', 'mcts'],
                        help='玩家2的AI类型')
    parser.add_argument('--tournament', action='store_true',
                        help='运行AI对战锦标赛')
    
    args = parser.parse_args()
    
    if args.tournament:
        run_tournament()
    else:
        main(args.ai1, args.ai2)