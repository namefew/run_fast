"""
强化学习环境模块
"""

import numpy as np
import random
from typing import List, Tuple, Dict, Any
from game import GameEngine
from cards import Card, CardPattern, CardType
from strategy import AIStrategy
import torch


class RLEnvironment:
    """强化学习环境"""
    
    def __init__(self):
        self.engine = GameEngine()
        self.state_size = self._get_state_size()
        self.action_size = 0  # 动作空间大小会动态变化
        self.current_state = None
        self.done = False
        # 检查是否有可用的GPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.verbose = False  # 默认关闭详细输出
    
    def reset(self) -> np.ndarray:
        """重置环境"""
        self.engine.reset()
        self.engine.deal_cards()
        self.current_state = self._get_state()
        self.done = False
        return self.current_state
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """执行动作"""
        # 将动作索引转换为实际出牌
        valid_patterns = self.engine.get_valid_patterns(self.engine.state.current_player)
        current_player = self.engine.state.current_player
        opponent_player = 1 - current_player

        # 添加动作有效性检查，防止无限循环
        if not valid_patterns and action != 0:
            action = 0  # 强制跳过

        # 打印当前状态（仅在详细模式下）
        if self.engine.state.last_pattern and self.verbose:
            print(f"上一手牌: {self.engine.state.last_pattern}")

        # 处理无效动作
        if action >= len(valid_patterns):
            return self._handle_invalid_action(valid_patterns, current_player)
        
        # 处理有效动作
        return self._handle_valid_action(valid_patterns, action, current_player)

    def _handle_invalid_action(self, valid_patterns, current_player):
        """处理无效动作"""
        if self.verbose:
            print(f"玩家 {current_player} 选择跳过 (动作无效，有效动作数: {len(valid_patterns)})")
        
        success = self.engine.pass_turn(self.engine.state.current_player)
        reward = 0.0
        
        if not success:
            # 不允许跳过，必须出牌
            if len(valid_patterns) > 0:
                # 强制执行第一个有效动作
                pattern = valid_patterns[0]
                if self.verbose:
                    print(f"玩家 {current_player} 被强制出牌: {pattern}")
                success = self.engine.play_cards(self.engine.state.current_player, pattern.cards)
                reward = self._calculate_reward(pattern) if success else -1.0
            else:
                # 真的没有有效动作，强制跳过
                self.engine.state.pass_count += 1
                self.engine.state.current_player = 1 - self.engine.state.current_player
                if self.engine.state.pass_count >= 2:
                    self.engine.state.last_pattern = None
                    self.engine.state.pass_count = 0
                reward = -1.0
        else:
            reward = -0.1  # 给予小的负奖励

        return self._finalize_step(reward)

    def _handle_valid_action(self, valid_patterns, action, current_player):
        """处理有效动作"""
        pattern = valid_patterns[action]
        
        if self.verbose:
            print(f"玩家 {current_player} 出牌: {pattern}")
        
        # 检查要出的牌是否在玩家手牌中
        player_hand = self.engine.state.players[current_player]
        cards_in_hand = all(card in player_hand for card in pattern.cards)
        
        if not cards_in_hand:
            return self._handle_missing_cards(valid_patterns, action, current_player)
        
        # 执行出牌
        return self._execute_play(pattern, current_player)

    def _handle_missing_cards(self, valid_patterns, action, current_player):
        """处理手牌不足的情况"""
        if self.verbose:
            print(f"错误：玩家 {current_player} 手牌中没有足够的牌")
        
        reward = -1.0
        # 尝试执行下一个有效动作
        if len(valid_patterns) > action + 1:
            pattern = valid_patterns[action + 1]
            if self.verbose:
                print(f"尝试下一个有效动作: {pattern}")
            success = self.engine.play_cards(self.engine.state.current_player, pattern.cards)
            reward = self._calculate_reward(pattern) if success else -1.0
        else:
            # 没有更多有效动作，跳过
            self.engine.pass_turn(self.engine.state.current_player)
            reward = -0.1
            
        return self._finalize_step(reward)

    def _execute_play(self, pattern, current_player):
        """执行出牌操作"""
        # 仅在详细模式下打印手牌信息
        if self.verbose:
            print(f"出牌前玩家 {current_player} 手牌: {sorted(self.engine.state.players[current_player])}")
            print(f"尝试出牌: {pattern}")
        
        success = self.engine.play_cards(self.engine.state.current_player, pattern.cards)
        
        if self.verbose:
            if success:
                print(f"出牌成功，出牌后玩家 {current_player} 手牌: {sorted(self.engine.state.players[current_player])}")
            else:
                print(f"出牌失败: {pattern}")
                print(f"玩家 {current_player} 手牌: {sorted(self.engine.state.players[current_player])}")
                print(f"尝试出的牌: {[str(card) for card in pattern.cards]}")
        
        reward = self._calculate_reward(pattern) if success else -1.0
        return self._finalize_step(reward)

    def _finalize_step(self, reward):
        """完成步骤，更新状态并返回结果"""
        # 更新状态
        self.current_state = self._get_state()
        self.done = self.engine.state.game_over
        
        # 如果游戏结束，给予最终奖励
        if self.done:
            reward += self._calculate_final_reward()
        
        info = {
            'winner': self.engine.state.winner if self.done else -1,
            'scores': self.engine.state.scores,
            'cards_left': self.engine.state.player_cards_left
        }
        
        return self.current_state, reward, self.done, info
    
    def _get_state_size(self) -> int:
        """计算状态空间大小"""
        # 状态包括：
        # 1. 己方手牌 (16张牌，每张牌用一个数字表示)
        # 2. 对手剩余牌数 (1个数字)
        # 3. 上一手牌型信息 (牌型类型、主点数、牌数)
        # 4. 是否首出 (1个数字)
        # 5. 已出牌统计 (16个数字，表示各点数已出牌数)
        return 16 + 1 + 3 + 1 + 16
    
    def _get_state(self) -> np.ndarray:
        """获取当前状态"""
        state = np.zeros(self.state_size)
        
        # 己方手牌 (简化表示，用点数表示牌)
        player_hand = self.engine.state.players[self.engine.state.current_player]
        for i, card in enumerate(player_hand[:16]):  # 最多16张牌
            state[i] = card.point
        
        # 对手剩余牌数
        opponent_id = 1 - self.engine.state.current_player
        state[16] = len(self.engine.state.players[opponent_id])
        
        # 上一手牌型信息
        if self.engine.state.last_pattern:
            state[17] = self.engine.state.last_pattern.type.value  # 牌型类型
            state[18] = self.engine.state.last_pattern.main_point   # 主点数
            state[19] = self.engine.state.last_pattern.card_count  # 牌数
        else:
            state[17] = 0
            state[18] = 0
            state[19] = 0
        
        # 是否首出
        state[20] = 1 if self.engine.state.last_pattern is None else 0
        
        # 未出现牌的统计信息 (各点数未出现牌数)
        # 索引21-36对应点数3-A,2的未出现牌数(0-4)
        point_counts = [0] * 16
        for card in self.engine.remaining_cards:
            point_index = card.point - 3  # 3对应索引0
            if 0 <= point_index < 16:
                point_counts[point_index] += 1
        
        for i in range(16):
            state[21 + i] = point_counts[i]
        
        return state
    
    def _calculate_reward(self, pattern: CardPattern) -> float:
        """计算即时奖励"""
        reward = 0.0
        
        # 根据出牌数给予奖励，出牌越多越好
        reward += pattern.card_count * 0.1
        
        # 如果是炸弹，给予额外奖励
        if pattern.type == CardType.BOMB:
            reward += 1.0
        
        # 如果是单张，给予小奖励
        if pattern.type == CardType.SINGLE :
            reward += 0.05
            
        # 基于已出牌统计的智能奖励
        if self._is_card_strongest(pattern):
            reward += 0.5  # 出最大的牌给予额外奖励
            
        # 基于对手管牌概率的奖励调整
        blocking_prob = self._calculate_blocking_probability(pattern)
        reward *= (1 - blocking_prob * 0.5)  # 对手越可能管住，奖励越低
        
        return reward
    
    def _is_card_strongest(self, pattern: CardPattern) -> bool:
        """判断当前牌是否可能是最大的"""
        if not pattern:
            return False
            
        # 获取对手可能的手牌
        opponent_cards = self._estimate_opponent_cards()
        
        # 如果无法估计对手手牌，返回False（保守估计）
        if not opponent_cards:
            return False
            
        point_counts = {}
        for card in opponent_cards:
            point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
        # 检查对手可能的手牌中是否存在能管住当前牌的牌型
        # 对于单张，检查是否存在更大的单张
        if pattern.type == CardType.SINGLE:
            for point, count in point_counts.items():
                if point > pattern.main_point:
                    return False  # 对手有更大的牌
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True
            
        # 对于其他牌型，需要检查对手是否可能有能管住的牌型
        elif pattern.type == CardType.PAIR:
            # 检查对手是否有更大的对子
            for point, count in point_counts.items():
                if count >= 2 and point > pattern.main_point:
                    return False
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True

        elif pattern.type == CardType.BOMB:
            # 炸弹只能被更大的炸弹管住
            for point, count in point_counts.items():
                if count >= 4 and point > pattern.main_point:
                    return False
                # 3张A也是炸弹，可以管住普通炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:  # 对手有A炸弹，当前不是A炸弹
                    return False
            return True
            
        elif pattern.type == CardType.THREE_WITH_TWO:
            for point, count in point_counts.items():
                if count >= 3 and point > pattern.main_point:
                    return False
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True
            
        elif pattern.type == CardType.STRAIGHT:
            for point, count in point_counts.items():
                if point > pattern.main_point:
                    # 检查对手是否有更大的顺子
                    # 对手需要有足够数量的连续牌才能组成更大的顺子
                    # 这里简化处理：如果有更大的牌，就认为可能组成更大的顺子
                    return False
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True
            
        elif pattern.type == CardType.DOUBLE_STRAIGHT:
            for point, count in point_counts.items():
                if count >= 2 and point > pattern.main_point:
                    # 检查对手是否有更大的连对
                    return False
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True
            
        elif pattern.type == CardType.AIRPLANE:
            for point, count in point_counts.items():
                if count >= 3 and point > pattern.main_point:
                    # 检查对手是否有更大的飞机
                    return False
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True
            
        elif pattern.type == CardType.AIRPLANE_WITH_WINGS:
            for point, count in point_counts.items():
                if count >= 3 and point > pattern.main_point:
                    # 检查对手是否有更大的飞机带翅膀
                    return False
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True
            
        elif pattern.type == CardType.FOUR_WITH_THREE:
            for point, count in point_counts.items():
                if count >= 4 and point > pattern.main_point:
                    # 检查对手是否有更大的四带三
                    return False
                if count == 4:  # 对手有炸弹
                    return False
                if point == 14 and count >= 3:  # 对手有A炸弹
                    return False
            return True
            
        # 对于其他牌型，简化处理：检查对手手牌数量是否足够组成更大的牌型
        else:
            opponent_hand_size = len(self.engine.state.players[1 - self.engine.state.current_player])
            if opponent_hand_size >= pattern.card_count:
                # 对手手牌数量足够，可能存在更大的牌型
                # 这里可以实现更复杂的逻辑来判断
                pass
        
        # 如果没有发现能管住当前牌的牌型，则当前牌可能是最大的
        return True
    
    def _calculate_blocking_probability(self, pattern: CardPattern) -> float:
        """计算对手管住当前牌的概率"""
        if not pattern:
            return 0.0
            
        # 获取对手可能的手牌
        opponent_cards = self._estimate_opponent_cards()
        opponent_hand_size = len(self.engine.state.players[1 - self.engine.state.current_player])
        
        # 如果对手没有手牌，无法管住
        if opponent_hand_size == 0:
            return 0.0
            
        # 基于对手可能的手牌计算管牌概率
        blocking_cards = 0
        total_cards = len(opponent_cards)
        
        if total_cards == 0:
            # 如果无法估计对手手牌，使用简化方法
            difficulty_factors = {
                CardType.SINGLE: 0.7,
                CardType.PAIR: 0.6,
                CardType.THREE_WITH_TWO: 0.4,
                CardType.STRAIGHT: 0.3,
                CardType.DOUBLE_STRAIGHT: 0.2,
                CardType.AIRPLANE: 0.2,
                CardType.AIRPLANE_WITH_WINGS: 0.2,
                CardType.BOMB: 0.1,
                CardType.FOUR_WITH_THREE: 0.3
            }
            
            difficulty = difficulty_factors.get(pattern.type, 0.5)
            hand_factor = min(opponent_hand_size / 16.0, 1.0)
            return difficulty * hand_factor
        
        # 计算对手可能的手牌中能管住当前牌的数量
        blocking_combinations = 0
        
        # 根据当前牌型类型进行不同的处理
        if pattern.type == CardType.SINGLE:
            for card in opponent_cards:
                # 创建一个单张牌型用于比较
                temp_pattern = CardPattern(CardType.SINGLE, [card], card.point)
                if temp_pattern.main_point > pattern.main_point:
                    blocking_cards += 1
                # 检查对手是否有炸弹
                point_counts = {}
                for c in opponent_cards:
                    point_counts[c.point] = point_counts.get(c.point, 0) + 1
                # 检查是否有炸弹
                if any(count >= 4 for count in point_counts.values()):
                    blocking_cards += 1
        elif pattern.type == CardType.PAIR:
            # 统计对手手牌中各点数的数量
            point_counts = {}
            for card in opponent_cards:
                point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
            # 检查对手是否有更大的对子
            for point, count in point_counts.items():
                if count >= 2 and point > pattern.main_point:
                    blocking_combinations += 1
                # 检查对手是否有炸弹
                if count >= 4:
                    blocking_combinations += 1
                # 检查对手是否有A炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:
                    blocking_combinations += 1
        elif pattern.type == CardType.THREE_WITH_TWO:
            # 统计对手手牌中各点数的数量
            point_counts = {}
            for card in opponent_cards:
                point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
            # 检查对手是否有更大的三同张
            for point, count in point_counts.items():
                if count >= 3 and point > pattern.main_point:
                    blocking_combinations += 1
                # 检查对手是否有炸弹
                if count >= 4:
                    blocking_combinations += 1
                # 检查对手是否有A炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:
                    blocking_combinations += 1
        elif pattern.type == CardType.STRAIGHT:
            # 对于顺子，检查对手是否有更大的顺子或炸弹
            point_counts = {}
            for card in opponent_cards:
                point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
            # 检查对手是否有炸弹
            for point, count in point_counts.items():
                if count >= 4:
                    blocking_combinations += 1
                # 检查对手是否有A炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:
                    blocking_combinations += 1
        elif pattern.type == CardType.DOUBLE_STRAIGHT:
            # 对于连对，检查对手是否有更大的连对或炸弹
            point_counts = {}
            for card in opponent_cards:
                point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
            # 检查对手是否有炸弹
            for point, count in point_counts.items():
                if count >= 4:
                    blocking_combinations += 1
                # 检查对手是否有A炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:
                    blocking_combinations += 1
        elif pattern.type == CardType.AIRPLANE:
            # 对于飞机，检查对手是否有更大的飞机或炸弹
            point_counts = {}
            for card in opponent_cards:
                point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
            # 检查对手是否有炸弹
            for point, count in point_counts.items():
                if count >= 4:
                    blocking_combinations += 1
                # 检查对手是否有A炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:
                    blocking_combinations += 1
        elif pattern.type == CardType.BOMB:
            # 对于炸弹，只检查是否有更大的炸弹
            point_counts = {}
            for card in opponent_cards:
                point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
            # 检查对手是否有更大的炸弹
            for point, count in point_counts.items():
                if count >= 4 and point > pattern.main_point:
                    blocking_combinations += 1
                # 检查对手是否有A炸弹且当前不是A炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:
                    blocking_combinations += 1
        elif pattern.type == CardType.FOUR_WITH_THREE:
            # 对于四带三，检查对手是否有炸弹
            point_counts = {}
            for card in opponent_cards:
                point_counts[card.point] = point_counts.get(card.point, 0) + 1
            
            # 检查对手是否有炸弹
            for point, count in point_counts.items():
                if count >= 4:
                    blocking_combinations += 1
                # 检查对手是否有A炸弹
                if point == 14 and count >= 3 and pattern.main_point < 14:
                    blocking_combinations += 1
        else:
            # 对于其他牌型，简化处理
            for card in opponent_cards:
                # 创建一个单张牌型用于比较
                temp_pattern = CardPattern(CardType.SINGLE, [card], card.point)
                if pattern.type == CardType.SINGLE and temp_pattern.main_point > pattern.main_point:
                    blocking_cards += 1
        
        # 基于能管住的牌数计算概率
        if blocking_combinations > 0:
            base_probability = min(blocking_combinations / max(len(opponent_cards), 1), 1.0)
        else:
            base_probability = blocking_cards / max(total_cards, 1)
        
        # 考虑牌型类型的影响
        type_factors = {
            CardType.SINGLE: 1.0,
            CardType.PAIR: 0.8,
            CardType.THREE_WITH_TWO: 0.6,
            CardType.STRAIGHT: 0.5,
            CardType.DOUBLE_STRAIGHT: 0.4,
            CardType.AIRPLANE: 0.4,
            CardType.AIRPLANE_WITH_WINGS: 0.4,
            CardType.BOMB: 0.2,
            CardType.FOUR_WITH_THREE: 0.5
        }
        
        type_factor = type_factors.get(pattern.type, 0.7)
        
        # 综合计算最终概率
        final_probability = base_probability * type_factor
        
        return min(final_probability, 1.0)
    
    def _estimate_opponent_cards(self) -> List[Card]:
        """估计对手可能的手牌"""
        # 基于未出现的牌和对手剩余牌数进行估计
        opponent_id = 1 - self.engine.state.current_player
        opponent_hand_size = len(self.engine.state.players[opponent_id])
        
        # 返回未出现的牌中的一部分作为对手可能的手牌
        # 这里可以实现更复杂的对手手牌推断逻辑
        return self.engine.remaining_cards[:opponent_hand_size]
    
    def _calculate_opponent_pattern_probability(self, pattern_type: CardType, card_count: int) -> float:
        """计算对手拥有特定牌型的概率"""
        if not pattern_type or card_count <= 0:
            return 0.0
        
        opponent_id = 1 - self.engine.state.current_player
        opponent_hand_size = len(self.engine.state.players[opponent_id])
        
        # 如果对手手牌数少于需要的牌数，则概率为0
        if opponent_hand_size < card_count:
            return 0.0
            
        # 基于未出现的牌计算概率
        # 这是一个简化的实现，实际可以使用组合数学进行更精确的计算
        remaining_cards_count = len(self.engine.remaining_cards)
        if remaining_cards_count == 0:
            return 0.0
            
        # 简化的概率计算
        # 假设对手随机从剩余牌中抽取手牌
        probability = min(1.0, card_count / remaining_cards_count)
        
        # 不同牌型有不同的基础概率
        base_probabilities = {
            CardType.SINGLE: 1.0,
            CardType.PAIR: 0.3,
            CardType.THREE_WITH_TWO: 0.1,
            CardType.STRAIGHT: 0.2,
            CardType.DOUBLE_STRAIGHT: 0.1,
            CardType.AIRPLANE: 0.05,
            CardType.AIRPLANE_WITH_WINGS: 0.05,
            CardType.BOMB: 0.02,
            CardType.FOUR_WITH_THREE: 0.05
        }
        
        base_prob = base_probabilities.get(pattern_type, 0.1)
        
        return probability * base_prob

    def _calculate_final_reward(self) -> float:
        """计算最终奖励"""
        if not self.done:
            return 0.0
        
        current_player = self.engine.state.current_player
        winner = self.engine.state.winner
        
        # 如果当前玩家获胜，给予大额正奖励
        if winner == current_player:
            if self.verbose:
                print(f"玩家 {current_player} 获胜!")
            return 10.0
        else:
            # 如果当前玩家失败，给予大额负奖励
            if self.verbose:
                print(f"玩家 {current_player} 失败!")
            return -10.0
    
    def get_valid_actions(self) -> List[int]:
        """获取有效动作列表"""
        valid_patterns = self.engine.get_valid_patterns(self.engine.state.current_player)
        # 添加调试信息
        # if len(valid_patterns) == 0 and self.engine.state.last_pattern is not None:
        #     player_id = self.engine.state.current_player
        #     opponent_id = 1 - player_id
        #     print(f"玩家{player_id}跳过")
        #     print(f"  玩家{player_id}手牌: {self.engine.state.players[player_id]}")
        #     print(f"  玩家{opponent_id}手牌: {self.engine.state.players[opponent_id]}")
        #     print(f"  上一手牌: {self.engine.state.last_pattern}")
        return list(range(len(valid_patterns)))
    
    def render(self):
        """渲染环境（用于调试）"""
        print(f"当前玩家: {self.engine.state.current_player}")
        print(f"玩家手牌: {self.engine.state.players[self.engine.state.current_player]}")
        if self.engine.state.last_pattern:
            print(f"上一手牌: {self.engine.state.last_pattern}")
        print(f"对手剩余牌数: {len(self.engine.state.players[1 - self.engine.state.current_player])}")


class CardGroupScorer:
    """牌型组合评分器，用于评估不同出牌策略的价值"""
    
    def __init__(self):
        pass
    
    def score_pattern(self, pattern: CardPattern, opponent_hand_size: int, 
                      known_opponent_cards: List[Card] = None, 
                      remaining_hand: List[Card] = None) -> float:
        """为牌型打分"""
        # 基础分数基于牌型和牌数
        base_score = self._get_base_score(pattern)
        
        # 计算被对手管住的概率
        block_probability = self._calculate_block_probability(pattern, opponent_hand_size, known_opponent_cards)
        
        # 考虑后续出牌的潜力
        future_potential = self._evaluate_future_potential(pattern)
        
        # 考虑剩余手牌的组合潜力
        remaining_potential = 0.0
        if remaining_hand:
            remaining_potential = self._evaluate_remaining_potential(remaining_hand, pattern.cards)
        
        # 综合评分
        final_score = base_score * (1 - block_probability) + future_potential + remaining_potential
        
        return final_score
    
    def _get_base_score(self, pattern: CardPattern) -> float:
        """获取牌型基础分数"""
        # 不同牌型有不同的基础价值
        base_scores = {
            CardType.SINGLE: 1.0,
            CardType.PAIR: 2.0,
            CardType.THREE_WITH_TWO: 3.0,
            CardType.STRAIGHT: 4.0,
            CardType.DOUBLE_STRAIGHT: 5.0,
            CardType.AIRPLANE: 6.0,
            CardType.AIRPLANE_WITH_WINGS: 6.5,
            CardType.BOMB: 10.0,
            CardType.FOUR_WITH_THREE: 7.0
        }
        
        score = base_scores.get(pattern.type, 1.0)
        
        # 考虑牌型大小
        if pattern.type in [CardType.SINGLE, CardType.PAIR, CardType.BOMB]:
            # 对于单张、对子和炸弹，点数越小价值越低
            score *= (15 - pattern.main_point) / 15.0
        
        # 考虑牌数，牌数越多越有价值
        score *= (pattern.card_count / 16.0)
        
        return score
    
    def _calculate_block_probability(self, pattern: CardPattern, opponent_hand_size: int,
                                     known_opponent_cards: List[Card] = None) -> float:
        """计算被对手管住的概率"""
        if not pattern:
            return 0.0
        
        # 如果没有上一手牌，不需要管牌
        # 这个函数主要用于评估主动出牌被管住的风险，而非跟牌
        
        # 简化处理：根据对手手牌数量和牌型类型估算
        if opponent_hand_size <= 0:
            return 0.0
        
        # 不同牌型被管住的难度不同
        difficulty_factors = {
            CardType.SINGLE: 0.7,
            CardType.PAIR: 0.6,
            CardType.THREE_WITH_TWO: 0.4,
            CardType.STRAIGHT: 0.3,
            CardType.DOUBLE_STRAIGHT: 0.2,
            CardType.AIRPLANE: 0.2,
            CardType.AIRPLANE_WITH_WINGS: 0.2,
            CardType.BOMB: 0.1,  # 炸弹很难被管住
            CardType.FOUR_WITH_THREE: 0.3
        }
        
        difficulty = difficulty_factors.get(pattern.type, 0.5)
        
        # 对手手牌越多，管住的概率越大
        hand_factor = min(opponent_hand_size / 16.0, 1.0)
        
        return difficulty * hand_factor
    
    def _evaluate_future_potential(self, pattern: CardPattern) -> float:
        """评估牌型的后续潜力"""
        # 炸弹具有很高的后续潜力
        if pattern.type == CardType.BOMB:
            return 5.0
        
        # 飞机和连对也具有不错的后续潜力
        if pattern.type in [CardType.AIRPLANE, CardType.AIRPLANE_WITH_WINGS, CardType.DOUBLE_STRAIGHT]:
            return 3.0
        
        # 单张和对子的后续潜力较低
        if pattern.type in [CardType.SINGLE, CardType.PAIR]:
            return 1.0
        
        # 其他牌型的后续潜力中等
        return 2.0
    
    def _evaluate_remaining_potential(self, hand: List[Card], played_cards: List[Card]) -> float:
        """评估剩余手牌的组合潜力"""
        if not hand:
            return 0.0
        
        # 计算剩余手牌
        remaining_cards = [card for card in hand if card not in played_cards]
        
        # 生成剩余手牌的所有可能牌型
        from game import GameEngine
        engine = GameEngine()
        engine.state.players[0] = remaining_cards
        
        # 创建一个临时的牌型列表
        potential_patterns = []
        engine._generate_all_patterns(remaining_cards, potential_patterns)
        
        # 评估剩余牌型的质量
        total_potential = 0.0
        for pattern in potential_patterns:
            # 基于牌型类型给予不同分数
            base_scores = {
                CardType.SINGLE: 0.5,
                CardType.PAIR: 1.0,
                CardType.THREE_WITH_TWO: 2.0,
                CardType.STRAIGHT: 2.5,
                CardType.DOUBLE_STRAIGHT: 3.0,
                CardType.AIRPLANE: 3.5,
                CardType.AIRPLANE_WITH_WINGS: 4.0,
                CardType.BOMB: 5.0,
                CardType.FOUR_WITH_THREE: 4.5
            }
            
            score = base_scores.get(pattern.type, 1.0)
            # 考虑牌数，牌数越多越有价值
            score *= (pattern.card_count / 16.0)
            total_potential += score
        
        # 返回平均潜力分数
        return total_potential / max(len(potential_patterns), 1) if potential_patterns else 0.0


# 测试代码
if __name__ == "__main__":
    env = RLEnvironment()
    state = env.reset()
    print(f"初始状态: {state}")
    print(f"使用设备: {env.device}")
    
    # 随机策略测试
    for i in range(10):
        if env.done:
            break
        
        valid_actions = env.get_valid_actions()
        if valid_actions:
            action = random.choice(valid_actions)
            state, reward, done, info = env.step(action)
            print(f"动作: {action}, 奖励: {reward}, 完成: {done}")
            env.render()
        else:
            print("没有有效动作")
            break