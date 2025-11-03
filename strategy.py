"""
AI玩家策略模块
"""

from typing import List, Tuple
from cards import Card, CardPattern, CardType
from game import GameEngine


class AIStrategy:
    """AI策略基类"""
    
    def __init__(self, player_id: int):
        self.player_id = player_id
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """
        选择行动
        返回: (action_type, cards)
        action_type: "play" 或 "pass"
        cards: 要出的牌列表
        """
        raise NotImplementedError


class SimpleAIStrategy(AIStrategy):
    """简单AI策略"""
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """基于规则的简单AI策略"""
        # 获取有效牌型
        valid_patterns = engine.get_valid_patterns(self.player_id)
        
        if not valid_patterns:
            # 没有可出的牌，只能跳过
            return ("pass", [])
        
        # 优先出能让自己尽快出完牌的牌型
        # 1. 如果只剩一张牌，必须出
        if len(engine.state.players[self.player_id]) == 1:
            return ("play", [engine.state.players[self.player_id][0]])
        
        # 2. 如果只剩两张牌且是对子，出对子
        if len(engine.state.players[self.player_id]) == 2:
            if valid_patterns and valid_patterns[0].type == CardType.PAIR:
                return ("play", valid_patterns[0].cards)
        
        # 3. 寻找最小的单张
        single_patterns = [p for p in valid_patterns if p.type == CardType.SINGLE]
        if single_patterns:
            # 选择点数最小的单张
            min_pattern = min(single_patterns, key=lambda p: p.main_point)
            return ("play", min_pattern.cards)
        
        # 4. 如果没有单张，出最小的牌型
        min_pattern = min(valid_patterns, key=lambda p: p.main_point)
        return ("play", min_pattern.cards)


class CardGroupScorer:
    """牌型组合评分器，用于评估不同出牌策略的价值"""
    
    def __init__(self):
        pass
    
    def score_pattern(self, pattern: CardPattern, opponent_hand_size: int, 
                      known_opponent_cards: List[Card] = None) -> float:
        """为牌型打分"""
        # 基础分数基于牌型和牌数
        base_score = self._get_base_score(pattern)
        
        # 计算被对手管住的概率
        block_probability = self._calculate_block_probability(pattern, opponent_hand_size, known_opponent_cards)
        
        # 考虑后续出牌的潜力
        future_potential = self._evaluate_future_potential(pattern)
        
        # 综合评分
        final_score = base_score * (1 - block_probability) + future_potential
        
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


class AdvancedAIStrategy(AIStrategy):
    """高级AI策略"""
    
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.scorer = CardGroupScorer()
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """基于更复杂规则的AI策略"""
        valid_patterns = engine.get_valid_patterns(self.player_id)
        
        if not valid_patterns:
            return ("pass", [])
        
        # 获取当前玩家手牌
        hand = engine.state.players[self.player_id]
        
        # 如果只剩一张牌，必须出
        if len(hand) == 1:
            return ("play", [hand[0]])
        
        # 分析当前局势
        is_first_move = engine.state.last_pattern is None
        is_opponent_about_to_win = len(engine.state.players[1 - self.player_id]) <= 2
        opponent_hand_size = len(engine.state.players[1 - self.player_id])
        
        # 为每个有效牌型评分
        pattern_scores = []
        for pattern in valid_patterns:
            score = self._score_pattern(pattern, engine, opponent_hand_size)
            pattern_scores.append((pattern, score))
        
        # 根据评分选择最佳牌型
        if pattern_scores:
            # 按评分排序
            pattern_scores.sort(key=lambda x: x[1], reverse=True)
            best_pattern = pattern_scores[0][0]
            return ("play", best_pattern.cards)
        
        # 如果评分系统失败，使用简单策略
        # 优先出单张小牌
        single_patterns = [p for p in valid_patterns if p.type == CardType.SINGLE]
        if single_patterns:
            # 避免出A和2，除非手牌很少
            if len(hand) > 5:
                safe_singles = [p for p in single_patterns if p.main_point < 14]
                if safe_singles:
                    min_pattern = min(safe_singles, key=lambda p: p.main_point)
                    return ("play", min_pattern.cards)
            
            min_pattern = min(single_patterns, key=lambda p: p.main_point)
            return ("play", min_pattern.cards)
        
        # 出最小的牌型
        if valid_patterns:
            min_pattern = min(valid_patterns, key=lambda p: p.main_point)
            return ("play", min_pattern.cards)
        
        return ("pass", [])
    
    def _score_pattern(self, pattern: CardPattern, engine: GameEngine, opponent_hand_size: int) -> float:
        """为牌型打分"""
        # 使用CardGroupScorer进行评分
        score = self.scorer.score_pattern(pattern, opponent_hand_size)
        
        # 考虑特殊策略因素
        hand = engine.state.players[self.player_id]
        
        # 如果是首出，偏向出中等牌型
        if engine.state.last_pattern is None:
            if pattern.type in [CardType.SINGLE, CardType.PAIR]:
                # 首出时避免出太小的牌
                if pattern.main_point < 8:
                    score *= 0.5
            elif pattern.type in [CardType.STRAIGHT, CardType.DOUBLE_STRAIGHT]:
                # 首出时优先考虑连牌
                score *= 1.2
        
        # 如果对手快赢了，优先出大牌
        if len(engine.state.players[1 - self.player_id]) <= 3:
            if pattern.type == CardType.BOMB:
                score *= 2.0  # 优先使用炸弹
            elif pattern.type == CardType.SINGLE and pattern.main_point >= 13:  # A, 2
                score *= 1.5
        
        # 考虑手牌剩余数量
        if len(hand) <= 5:
            # 手牌较少时，优先出牌数多的牌型
            score *= (1.0 + pattern.card_count / 10.0)
        
        return score


class MLBasedAIStrategy(AIStrategy):
    """基于机器学习的AI策略（占位）"""
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """基于机器学习的AI策略"""
        # 这里可以实现更复杂的基于机器学习的策略
        # 目前先使用高级策略作为替代
        advanced_strategy = AdvancedAIStrategy(self.player_id)
        return advanced_strategy.choose_action(engine)


if __name__ == "__main__":
    # 测试代码
    pass
