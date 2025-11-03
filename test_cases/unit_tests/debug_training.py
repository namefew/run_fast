"""
调试训练过程中的卡顿问题
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from game import GameEngine
from cards import Card, Suit, CardPattern, CardType
from rl_environment import RLEnvironment
from human_strategy import HumanStrategy
from rl_strategy import DQNAIStrategy
import random

def debug_training_loop():
    """调试训练循环"""
    print("=== 调试训练循环 ===")
    
    # 创建环境和AI
    env = RLEnvironment()
    env.verbose = True  # 启用详细输出
    agent = DQNAIStrategy(player_id=0, state_size=env.state_size)
    human_strategy = HumanStrategy(player_id=1)
    
    # 重置环境
    state = env.reset()
    print(f"初始状态: {state}")
    print(f"玩家0手牌数: {len(env.engine.state.players[0])}")
    print(f"玩家1手牌数: {len(env.engine.state.players[1])}")
    
    # 限制最大步数以防止无限循环
    max_steps = 50
    step_count = 0
    
    while not env.done and step_count < max_steps:
        current_player = env.engine.state.current_player
        print(f"\n--- 步骤 {step_count + 1} ---")
        print(f"当前玩家: {current_player}")
        print(f"上一手牌: {env.engine.state.last_pattern}")
        print(f"玩家{current_player}手牌: {sorted(env.engine.state.players[current_player])}")
        
        if current_player == 0:  # DQN AI玩家
            print("DQN AI 玩家行动")
            valid_actions = env.get_valid_actions()
            print(f"有效动作数: {len(valid_actions)}")
            
            if not valid_actions:
                print("没有有效动作，跳过")
                next_state, reward, done, info = env.step(0)
            else:
                # 使用简单策略选择动作
                action = random.choice(valid_actions)
                print(f"选择动作: {action}")
                next_state, reward, done, info = env.step(action)
                
            state = next_state
            print(f"奖励: {reward}")
            
        else:  # HumanStrategy玩家
            print("HumanStrategy 玩家行动")
            action_type, cards = human_strategy.choose_action(env.engine)
            print(f"选择动作: {action_type}, 牌: {[str(card) for card in cards]}")
            
            # 转换为环境可理解的动作
            if action_type == "pass":
                print("执行跳过")
                next_state, reward, done, info = env.step(0)
            else:
                # 找到对应的牌型动作索引
                valid_patterns = env.engine.get_valid_patterns(current_player)
                print(f"有效牌型数: {len(valid_patterns)}")
                
                action = 0  # 默认为0
                found = False
                for i, pattern in enumerate(valid_patterns):
                    # 比较牌型的牌是否相同
                    if set(str(card) for card in pattern.cards) == set(str(card) for card in cards):
                        action = i
                        found = True
                        print(f"找到匹配动作: {action}")
                        break
                
                if not found:
                    print("未找到匹配动作，使用默认动作0")
                    action = 0 if valid_patterns else 0
                    
                next_state, reward, done, info = env.step(action)
                
            state = next_state
            print(f"奖励: {reward}")
        
        step_count += 1
        print(f"游戏是否结束: {env.done}")
        
        if env.done:
            print(f"游戏结束，赢家: {env.engine.state.winner}")
            break
    
    if step_count >= max_steps:
        print("达到最大步数限制，强制退出")

if __name__ == "__main__":
    debug_training_loop()