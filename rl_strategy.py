"""
基于强化学习的AI策略模块
"""

import numpy as np
import random
from typing import List, Tuple, Dict, Any
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from game import GameEngine
from cards import Card, CardPattern
from human_strategy import HumanStrategy
from strategy import AIStrategy
from rl_environment import RLEnvironment, CardGroupScorer


class DQN(nn.Module):
    """深度Q网络"""
    
    def __init__(self, state_size: int, action_size: int):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, action_size)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x


class DQNAIStrategy(AIStrategy):
    """基于深度Q网络的AI策略"""
    
    def __init__(self, player_id: int, state_size: int = 21, lr: float = 0.001):
        super().__init__(player_id)
        self.state_size = state_size
        self.action_size = 200  # 增加动作空间大小，实际会动态调整
        
        # 检查是否有可用的GPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Q网络
        self.q_network = DQN(state_size, self.action_size).to(self.device)
        self.target_network = DQN(state_size, self.action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        
        # 经验回放
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # 训练参数
        self.gamma = 0.95  # 折扣因子
        self.epsilon = 1.0  # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = lr
        self.tau = 0.001  # 软更新参数
        
        # 更新目标网络
        self._update_target_network()
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """选择动作"""
        # 获取有效牌型
        valid_patterns = engine.get_valid_patterns(self.player_id)
        
        if not valid_patterns:
            return ("pass", [])
        
        # 获取当前状态
        env = RLEnvironment()
        env.engine = engine
        state = env._get_state()
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        # epsilon-贪婪策略
        if np.random.random() <= self.epsilon:
            # 使用启发式方法选择动作而不是完全随机
            action_idx = self._heuristic_action_selection(valid_patterns, engine)
        else:
            # 使用Q网络选择最优动作
            self.q_network.eval()
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
                # 只考虑有效动作
                valid_q_values = q_values[0][:len(valid_patterns)]
                if len(valid_q_values) > 0:
                    action_idx = valid_q_values.argmax().item()
                else:
                    action_idx = 0
            self.q_network.train()
        
        # 将动作索引转换为实际出牌
        if action_idx >= len(valid_patterns):
            return ("pass", [])
        
        pattern = valid_patterns[action_idx]
        return ("play", pattern.cards)
    
    def _heuristic_action_selection(self, valid_patterns: List[CardPattern], engine: GameEngine) -> int:
        """使用启发式方法选择动作，而不是完全随机"""
        # 使用评分器为每个有效牌型评分
        scorer = CardGroupScorer()
        opponent_id = 1 - self.player_id
        opponent_hand_size = len(engine.state.players[opponent_id])
        
        # 获取当前玩家手牌
        player_hand = engine.state.players[self.player_id]
        
        # 为每个有效牌型评分
        scores = []
        for pattern in valid_patterns:
            score = scorer.score_pattern(pattern, opponent_hand_size, remaining_hand=player_hand)
            scores.append(score)
        
        # 使用softmax将分数转换为概率分布
        scores = np.array(scores)
        # 为避免数值溢出，减去最大值
        if len(scores) > 0:
            scores = scores - np.max(scores)
            exp_scores = np.exp(scores)
            probabilities = exp_scores / np.sum(exp_scores)
            
            # 根据概率分布选择动作
            action_idx = np.random.choice(len(valid_patterns), p=probabilities)
        else:
            action_idx = 0
        return action_idx

    def remember(self, state, action, reward, next_state, done):
        """将经验存储到回放内存中"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """经验回放训练"""
        if len(self.memory) < self.batch_size:
            return
        
        # 从回放内存中随机采样一批经验
        batch = random.sample(self.memory, self.batch_size)
        
        # 优化：将列表转换为numpy数组再转换为tensor，避免警告
        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])
        
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.BoolTensor(dones).to(self.device)
        
        # 计算当前Q值，确保动作索引不会越界
        q_values = self.q_network(states)
        # 检查动作索引是否在有效范围内
        max_actions = q_values.size(1)
        clamped_actions = torch.clamp(actions, 0, max_actions - 1)
        current_q_values = q_values.gather(1, clamped_actions.unsqueeze(1))
        
        # 计算目标Q值
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # 计算损失并更新网络
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        # 添加梯度裁剪防止梯度爆炸
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
        self.optimizer.step()
        
        # 降低探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def _update_target_network(self):
        """软更新目标网络"""
        for target_param, param in zip(self.target_network.parameters(), self.q_network.parameters()):
            target_param.data.copy_(self.tau * param.data + (1.0 - self.tau) * target_param.data)


class PPOAIStrategy(AIStrategy):
    """基于PPO(近端策略优化)的AI策略"""
    
    def __init__(self, player_id: int, state_size: int = 21):
        super().__init__(player_id)
        self.state_size = state_size
        # 检查是否有可用的GPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        # PPO实现可以在这里添加
        # 为简化起见，这里只是占位符
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """选择动作"""
        # 获取有效牌型
        valid_patterns = engine.get_valid_patterns(self.player_id)
        
        if not valid_patterns:
            return ("pass", [])
        
        # 使用某种策略选择动作
        # 这里可以使用策略网络来选择动作
        scorer = CardGroupScorer()
        opponent_id = 1 - self.player_id
        opponent_hand_size = len(engine.state.players[opponent_id])
        
        # 获取当前玩家手牌
        player_hand = engine.state.players[self.player_id]
        
        # 为每个有效牌型评分
        scores = []
        for pattern in valid_patterns:
            score = scorer.score_pattern(pattern, opponent_hand_size, remaining_hand=player_hand)
            scores.append(score)
        
        # 选择评分最高的牌型
        best_idx = np.argmax(scores)
        best_pattern = valid_patterns[best_idx]
        
        return ("play", best_pattern.cards)


class MonteCarloAIStrategy(AIStrategy):
    """基于蒙特卡洛树搜索的AI策略"""
    
    def __init__(self, player_id: int, simulations: int = 100):
        super().__init__(player_id)
        self.simulations = simulations
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """使用蒙特卡洛树搜索选择动作"""
        # 获取有效牌型
        valid_patterns = engine.get_valid_patterns(self.player_id)
        
        if not valid_patterns:
            return ("pass", [])
        
        # 如果只有一个选择，直接返回
        if len(valid_patterns) == 1:
            return ("play", valid_patterns[0].cards)
        
        # 对每个动作进行模拟
        action_scores = []
        for pattern in valid_patterns:
            score = self._simulate_action(engine, pattern)
            action_scores.append(score)
        
        # 选择得分最高的动作
        best_idx = np.argmax(action_scores)
        return ("play", valid_patterns[best_idx].cards)
    
    def _simulate_action(self, engine: GameEngine, pattern: CardPattern) -> float:
        """模拟执行某个动作的结果"""
        total_score = 0.0
        
        # 进行多次模拟
        for _ in range(self.simulations):
            # 创建副本
            engine_copy = GameEngine()
            engine_copy.state = engine.state  # 简化处理，实际应深拷贝
            
            # 执行动作
            success = engine_copy.play_cards(self.player_id, pattern.cards)
            if not success:
                total_score -= 10.0  # 失败给予负分
                continue
            
            # 模拟游戏直到结束
            while not engine_copy.state.game_over:
                current_player = engine_copy.state.current_player
                # 使用随机策略模拟对手
                valid_patterns_op = engine_copy.get_valid_patterns(current_player)
                if valid_patterns_op:
                    chosen_pattern = random.choice(valid_patterns_op)
                    engine_copy.play_cards(current_player, chosen_pattern.cards)
                else:
                    engine_copy.pass_turn(current_player)
            
            # 根据结果评分
            if engine_copy.state.winner == self.player_id:
                total_score += 1.0
            else:
                total_score -= 1.0
        
        return total_score / self.simulations


# 训练函数
def train_dqn_agent(episodes: int = 1000):
    """训练DQN智能体"""
    env = RLEnvironment()
    env.verbose = False  # 禁用详细输出以提高训练速度
    state_size = env.state_size
    agent = DQNAIStrategy(player_id=0, state_size=state_size)
    human_strategy = HumanStrategy(player_id=1)  # 创建HumanStrategy实例用于1号玩家
    
    scores = deque(maxlen=100)
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        steps = 0
        
        # 添加调试计数器，防止无限循环
        max_steps_per_episode = 1000  # 设置合理的最大步数
        step_count = 0
        
        # 用于详细调试的信息
        debug_info = []
        
        while not env.done and step_count < max_steps_per_episode:
            current_player = env.engine.state.current_player
            
            # 根据当前玩家选择不同的策略
            if current_player == 0:  # DQN AI玩家
                # 获取有效动作
                valid_actions = env.get_valid_actions()
                if not valid_actions:
                    # 没有有效动作，只能跳过
                    next_state, reward, done, info = env.step(0)
                    steps += 1
                    step_count += 1
                    total_reward += reward
                    state = next_state
                    debug_info.append(f"玩家0跳过，无有效动作")
                    continue
                
                # 使用epsilon-贪婪策略选择动作
                if random.random() <= agent.epsilon:
                    # 探索：使用启发式方法选择动作
                    valid_patterns = env.engine.get_valid_patterns(env.engine.state.current_player)
                    if valid_patterns:
                        action = agent._heuristic_action_selection(valid_patterns, env.engine)
                    else:
                        action = 0
                else:
                    # 利用：使用Q网络选择最优动作
                    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(agent.device)
                    agent.q_network.eval()
                    with torch.no_grad():
                        q_values = agent.q_network(state_tensor)
                        # 确保只考虑有效的动作
                        valid_q_values = q_values[0][:min(len(valid_actions), q_values.size(1))]
                        if len(valid_q_values) > 0:
                            action = valid_q_values.argmax().item()
                        else:
                            action = 0
                    agent.q_network.train()
                
                # 执行动作
                next_state, reward, done, info = env.step(action)
                total_reward += reward
                
                # 存储经验
                agent.remember(state, action, reward, next_state, done)
                
                # 训练网络
                agent.replay()
                
                state = next_state
                steps += 1
                step_count += 1
                
                debug_info.append(f"玩家0执行动作: {action}, 奖励: {reward:.2f}, 手牌数: {len(env.engine.state.players[0])}")
                
            else:  # HumanStrategy玩家 (1号玩家)
                # 使用HumanStrategy选择动作
                try:
                    action_type, cards = human_strategy.choose_action(env.engine)
                except Exception as e:
                    print(f"玩家1选择动作时出错: {e}")
                    # 出错时默认跳过
                    next_state, reward, done, info = env.step(0)
                    state = next_state
                    steps += 1
                    step_count += 1
                    debug_info.append(f"玩家1出错跳过")
                    continue
                
                # 将动作转换为环境可以理解的格式
                if action_type == "pass":
                    # 执行跳过动作
                    next_state, reward, done, info = env.step(0)  # 跳过通常对应动作0
                    debug_info.append(f"玩家1跳过")
                else:
                    # 找到对应的牌型动作索引
                    valid_patterns = env.engine.get_valid_patterns(current_player)
                    action = 0  # 默认为0
                    found = False
                    for i, pattern in enumerate(valid_patterns):
                        # 比较牌型的牌是否相同
                        if set(str(card) for card in pattern.cards) == set(str(card) for card in cards):
                            action = i
                            found = True
                            break
                    
                    # 如果没找到匹配的动作，使用启发式方法选择一个动作
                    if not found and len(valid_patterns) > 0:
                        # 使用HumanStrategy的启发式方法选择一个动作
                        scorer = CardGroupScorer()
                        opponent_id = 1 - current_player
                        opponent_hand_size = len(env.engine.state.players[opponent_id])
                        player_hand = env.engine.state.players[current_player]
                        
                        # 为每个有效牌型评分
                        scores_list = []
                        for pattern in valid_patterns:
                            try:
                                score = scorer.score_pattern(pattern, opponent_hand_size, remaining_hand=player_hand)
                                scores_list.append(score)
                            except Exception as e:
                                print(f"评分牌型时出错 {pattern}: {e}")
                                scores_list.append(0)  # 出错时给0分
                        
                        # 选择评分最高的牌型
                        if scores_list:
                            best_idx = np.argmax(scores_list)
                            action = best_idx
                        else:
                            action = 0
                    elif not found:
                        # 没有有效动作，只能跳过
                        next_state, reward, done, info = env.step(0)
                        state = next_state
                        steps += 1
                        step_count += 1
                        debug_info.append(f"玩家1跳过，无有效动作")
                        continue
                    
                    # 执行动作
                    next_state, reward, done, info = env.step(action)
                    debug_info.append(f"玩家1执行动作: {action}, 出牌: {[str(card) for card in cards]}, 奖励: {reward:.2f}, 手牌数: {len(env.engine.state.players[1])}")
                
                state = next_state
                steps += 1
                step_count += 1
            
            if done:
                break
        
        # 检查是否因为达到最大步数而退出循环
        if step_count >= max_steps_per_episode:
            print(f"警告: 第 {episode} 轮游戏因达到最大步数限制而强制结束")
            # 打印详细调试信息
            print(f"游戏状态详情:")
            print(f"  玩家0手牌数: {len(env.engine.state.players[0])}")
            print(f"  玩家1手牌数: {len(env.engine.state.players[1])}")
            print(f"  上一手牌: {env.engine.state.last_pattern}")
            print(f"  当前玩家: {env.engine.state.current_player}")
            print(f"  跳过次数: {env.engine.state.pass_count}")
            print(f"  玩家0手牌: {sorted(env.engine.state.players[0])}")
            print(f"  玩家1手牌: {sorted(env.engine.state.players[1])}")
            print(f"  最后几步动作:")
            for info in debug_info[-20:]:  # 打印最后20步动作
                print(f"    {info}")
        
        scores.append(total_reward)
        
        # 更新目标网络（仅对DQN AI玩家）
        agent._update_target_network()
        
        # 降低探索率
        if agent.epsilon > agent.epsilon_min:
            agent.epsilon *= agent.epsilon_decay
        
        # 打印进度（减少输出频率）
        # if episode % 100 == 0:  # 每100轮输出一次
        avg_score = np.mean(scores) if scores else 0
        print(f"回合: {episode}, 平均得分: {avg_score:.4f}, Epsilon: {agent.epsilon:.4f}")

        # 检查是否提前收敛
        if episode > 1000 and len(scores) >= 100:  # 移除平均得分限制，避免过早收敛
            avg_score = np.mean(scores)
            if avg_score > 50:
                print(f"提前收敛于第 {episode} 回合")
                break
    
    print("训练完成!")
    return agent


if __name__ == "__main__":
    # 训练示例
    # agent = train_dqn_agent(1000)
    pass