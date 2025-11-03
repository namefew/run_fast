"""
强化学习AI训练脚本
"""

import argparse
import torch
import numpy as np
from rl_strategy import train_dqn_agent
from rl_environment import RLEnvironment
from human_strategy import HumanStrategy  # 添加导入


def train_dqn(episodes=1000, save_path="models/dqn_model.pth"):
    """训练DQN模型"""
    print(f"开始训练DQN模型，共{episodes}轮")
    print(f"使用设备: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    
    # 训练模型
    agent = train_dqn_agent(episodes)
    
    # 保存模型
    torch.save(agent.q_network.state_dict(), save_path)
    print(f"模型已保存到 {save_path}")
    
    return agent


def evaluate_agent(agent, episodes=100):
    """评估AI性能"""
    print(f"评估AI性能，共{episodes}轮游戏")
    
    env = RLEnvironment()
    wins = 0
    total_scores = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        
        while not env.done:
            # 选择动作
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                env.step(0)  # 跳过
                continue
            
            # 使用训练好的模型选择动作
            if hasattr(agent, 'q_network'):
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(agent.device)
                agent.q_network.eval()
                with torch.no_grad():
                    q_values = agent.q_network(state_tensor)
                    valid_q_values = q_values[0][:len(valid_actions)]
                    action = valid_q_values.argmax().item()
                agent.q_network.train()
            else:
                action = np.random.choice(valid_actions)
            
            # 执行动作
            state, reward, done, info = env.step(action)
            total_reward += reward
        
        total_scores.append(total_reward)
        if info['winner'] == 0:  # 假设训练的AI是玩家0
            wins += 1
    
    win_rate = wins / episodes
    avg_score = np.mean(total_scores)
    
    print(f"胜率: {win_rate:.2%}")
    print(f"平均得分: {avg_score:.2f}")
    
    return win_rate, avg_score


def main():
    parser = argparse.ArgumentParser(description='训练跑得快AI')
    parser.add_argument('--algorithm', type=str, default='dqn', 
                        choices=['dqn', 'ppo', 'a3c'],
                        help='强化学习算法')
    parser.add_argument('--episodes', type=int, default=100000,
                        help='训练轮数')
    parser.add_argument('--save_path', type=str, default='models/dqn_model.pth',
                        help='模型保存路径')
    parser.add_argument('--evaluate', action='store_true',
                        help='是否评估模型')
    
    args = parser.parse_args()
    
    if args.algorithm == 'dqn':
        agent = train_dqn(args.episodes, args.save_path)
        
        # if args.evaluate:
        evaluate_agent(agent)


if __name__ == "__main__":
    main()