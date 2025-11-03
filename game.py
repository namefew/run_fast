"""
跑得快游戏引擎
"""

import random
from typing import List, Optional
from cards import Card, Suit, CardType, CardPattern, create_deck, detect_card_type, compare_patterns
from collections import defaultdict

class GameState:
    """游戏状态"""
    def __init__(self):
        self.deck: List[Card] = []  # 牌堆
        self.players: List[List[Card]] = [[], []]  # 两个玩家的手牌
        self.current_player: int = 0  # 当前玩家（0或1）
        self.last_pattern: Optional[CardPattern] = None  # 上一手牌
        self.last_player: int = -1  # 最后出牌的玩家
        self.pass_count: int = 0  # 连续跳过次数
        self.game_over: bool = False  # 游戏是否结束
        self.winner: int = -1  # 赢家
        self.first_player: int = -1  # 首出牌玩家
        self.scores: List[int] = [0, 0]  # 玩家得分
        self.is_first_round: bool = True  # 是否是第一轮
        self.player_cards_left: List[int] = [16, 16]  # 玩家剩余牌数


class GameEngine:
    """游戏引擎"""
    
    def __init__(self):
        self.state = GameState()
        self.base_score = 10  # 底分
        self.game_history = []  # 游戏历史记录，用于强化学习
        self.remaining_cards = []  # 未出现的牌（完整的牌堆减去已知的牌）
    
    def deal_cards(self):
        """发牌"""
        # 创建并洗牌
        self.state.deck = create_deck()
        random.shuffle(self.state.deck)
        
        # 发牌给两个玩家，每人16张
        for i in range(16):
            self.state.players[0].append(self.state.deck.pop())
            self.state.players[1].append(self.state.deck.pop())
        
        # 排序手牌
        self.state.players[0].sort()
        self.state.players[1].sort()
        
        # 确定首出牌玩家（有黑桃3的玩家先出牌，否则是红桃3）
        self.state.first_player = self._determine_first_player()
        self.state.current_player = self.state.first_player
        
        # 初始化未出现的牌（完整的牌堆减去双方手牌）
        self._update_remaining_cards()
    
    def _determine_first_player(self) -> int:
        """确定首出牌玩家"""
        spade_3 = Card(Suit.SPADE, '3')
        heart_3 = Card(Suit.HEART, '3')
        
        # 检查是否有玩家有黑桃3
        for i in range(2):
            if spade_3 in self.state.players[i]:
                return i
        
        # 检查是否有玩家有红桃3
        for i in range(2):
            if heart_3 in self.state.players[i]:
                return i
        
        # 默认玩家0先出牌
        return 0
    
    def play_cards(self, player_id: int, cards: List[Card]) -> bool:
        """玩家出牌"""
        # 清除缓存，因为手牌状态改变了
        if hasattr(self, '_valid_patterns_cache'):
            self._valid_patterns_cache.clear()
            
        if player_id != self.state.current_player:
            return False
        
        # 检查玩家是否有这些牌
        player_hand = self.state.players[player_id]
        if not all(card in player_hand for card in cards):
            return False
        
        # 创建牌型对象
        pattern = self._create_card_pattern(cards)
        if not pattern:
            return False
        
        # 检查是否符合出牌规则
        if not self._is_valid_play(pattern):
            return False
        
        # 移除玩家手牌
        for card in cards:
            if card in player_hand:  # 确保牌在玩家手中
                player_hand.remove(card)
            else:
                # 牌不在玩家手中，出牌失败
                return False
        
        # 更新游戏状态
        self.state.last_pattern = pattern
        self.state.pass_count = 0
        self.state.player_cards_left[player_id] = len(player_hand)
        
        # 检查游戏是否结束
        if len(player_hand) == 0:
            self.state.game_over = True
            self.state.winner = player_id
            self.state.scores[player_id] += 1
        
        # 切换到下一个玩家
        print(f"{player_id} - {self.state.players[self.state.current_player]} - 出牌：{pattern.cards}")
        self.state.current_player = 1 - player_id
        return True

    def pass_turn(self, player_id: int) -> bool:
        """玩家跳过"""
        # 清除缓存，因为游戏状态改变了
        if hasattr(self, '_valid_patterns_cache'):
            self._valid_patterns_cache.clear()
            
        if player_id != self.state.current_player:
            return False
        
        self.state.pass_count += 1
        self.state.current_player = 1 - player_id
        
        # 如果连续跳过两次，清空上一手牌记录
        if self.state.pass_count >= 2:
            self.state.last_pattern = None
            self.state.pass_count = 0
        
        return True
    
    def _is_valid_play(self, pattern: CardPattern) -> bool:
        """检查是否符合出牌规则"""
        # 如果是首出或者上家跳过，任何有效牌型都可以出
        if not self.is_cover_play():
            return True
        
        # 否则必须能管住上一手牌
        result = compare_patterns(pattern, self.state.last_pattern)
        return result
    
    def _update_remaining_cards(self):
        """更新未出现的牌列表"""
        # 创建完整的牌堆
        full_deck = create_deck()
        
        # 从完整牌堆中移除已知的牌：
        # 1. 己方手牌
        # 2. 对手已出的牌（通过game_history获取）
        known_cards = set()
        
        # 添加己方手牌
        for card in self.state.players[self.state.current_player]:
            known_cards.add(card)
        
        # 添加对手已出的牌
        opponent_id = 1 - self.state.current_player
        for move in self.game_history:
            if move['player'] == opponent_id:
                for card in move['cards']:
                    known_cards.add(card)
        
        # 计算剩余未出现的牌（对手手上的牌+还在牌堆中的牌）
        self.remaining_cards = [card for card in full_deck if card not in known_cards]
    
    def get_valid_patterns(self, player_id: int) -> List[CardPattern]:
        """获取玩家可以出的所有有效牌型"""
        # 检查缓存
        cache_key = (player_id, tuple(sorted(self.state.players[player_id])), self.state.last_pattern, self.state.pass_count)
        if hasattr(self, '_valid_patterns_cache') and cache_key in self._valid_patterns_cache:
            return self._valid_patterns_cache[cache_key]
            
        valid_patterns = []
        player_hand = self.state.players[player_id]
        
        # 生成所有可能的牌型组合
        self.generate_all_patterns(player_hand, valid_patterns)
        
        # 如果不是首出且上家没有跳过，只保留能管住上一手牌的牌型
        if self.is_cover_play():
            valid_patterns = [p for p in valid_patterns if compare_patterns(p, self.state.last_pattern)]
        
        # 缓存结果
        if not hasattr(self, '_valid_patterns_cache'):
            self._valid_patterns_cache = {}
        self._valid_patterns_cache[cache_key] = valid_patterns
        
        return valid_patterns

    def get_valid_pattern_groups(self, player_id: int) -> List[List[CardPattern]]:
        """
        获取玩家可以出的所有有效牌型组合分组
        
        Args:
            player_id: 玩家ID
            
        Returns:
            List[List[CardPattern]]: 所有有效的牌型组合分组
        """
        # 获取玩家手牌
        player_hand = self.state.players[player_id]
        
        # 生成所有可能的牌型组合
        all_patterns = []
        self.generate_all_patterns(player_hand, all_patterns)
        
        # 将牌型组合分组
        pattern_groups = self.group_patterns_into_hands(player_hand, all_patterns)
        
        # 按分组的size排序，短的在前
        pattern_groups.sort(key=len)
        
        # 如果不是首出且上家没有跳过，只保留包含能管住上一手牌的牌型的分组
        if self.is_cover_play():
            valid_groups = []
            for group in pattern_groups:
                # 检查组中是否有能管住上一手牌的牌型
                can_beat = any(compare_patterns(pattern, self.state.last_pattern) for pattern in group)
                if can_beat:
                    valid_groups.append(group)
            pattern_groups = valid_groups
            
            # 重新按分组的size排序，短的在前
            pattern_groups.sort(key=len)
            
        # 限制返回的分组数量，避免过多分组导致性能问题
        return pattern_groups

    def group_patterns_into_hands(self, hand: List[Card], patterns: List[CardPattern]) -> List[List[CardPattern]]:
        """
        将牌型组合分组，每组构成一个完整手牌
        
        Args:
            hand: 玩家手牌
            patterns: 所有可能的牌型
            
        Returns:
            List[List[CardPattern]]: 分组后的牌型组合
        """
        if not patterns:
            return []
            
        # 创建一个字典来跟踪每张牌在哪些牌型中出现
        card_to_patterns = defaultdict(list)
        for i, pattern in enumerate(patterns):
            for card in pattern.cards:
                card_to_patterns[card].append(i)
        
        # 使用回溯算法将牌型分组
        groups = []
        used_patterns = set()
        
        def backtrack(current_group, used_cards):
            # 如果所有牌都已使用，添加当前分组
            if len(used_cards) == len(hand):
                groups.append(current_group[:])
                return len(groups) >= 300  # 限制最多100个分组
            
            # 找到第一个未使用的牌
            next_card = None
            for card in hand:
                if card not in used_cards:
                    next_card = card
                    break
            
            if next_card is None:
                return False
                
            # 尝试包含该牌的每个牌型
            for pattern_idx in card_to_patterns[next_card]:
                if pattern_idx in used_patterns:
                    continue
                    
                pattern = patterns[pattern_idx]
                # 检查该牌型的所有牌是否都未使用
                if all(card not in used_cards for card in pattern.cards):
                    # 添加该牌型到当前分组
                    current_group.append(pattern)
                    used_patterns.add(pattern_idx)
                    new_used_cards = used_cards.union(set(pattern.cards))
                    
                    # 递归处理
                    if backtrack(current_group, new_used_cards):
                        return True
                        
                    # 回溯
                    current_group.pop()
                    used_patterns.remove(pattern_idx)
            
            return False
        
        # 开始回溯，限制最多生成100个分组
        backtrack([], set())
        
        return groups

    def is_cover_play(self):
        return self.state.last_pattern is not None and self.state.pass_count == 0

    def reset(self):
        """重置游戏状态"""
        # 清除缓存
        if hasattr(self, '_valid_patterns_cache'):
            self._valid_patterns_cache.clear()
            
        self.state = GameState()
        self.deck = create_deck()
    
    def get_player_cards_count(self):
        """获取玩家剩余手牌数"""
        return [len(self.state.players[0]), len(self.state.players[1])]

    def generate_all_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成所有可能的牌型组合"""
        # 优化：根据手牌数量决定生成哪些牌型
        hand_size = len(hand)

        # 按照优先级顺序生成牌型：炸弹 > 飞机带翅膀 > 飞机 > 顺子 > 连对 > 三带二 > 对子 > 单张
        
        # 生成炸弹（优先级最高）
        self._generate_bomb_patterns(hand, patterns)
        
        # 生成四带三
        # if hand_size >= 4:
        #     self._generate_four_with_three_patterns(hand, patterns)
        
        # 生成飞机带翅膀
        if hand_size >= 7:
            self._generate_airplane_with_wings_patterns(hand, patterns)
        
        # 生成飞机
        # if hand_size >= 6:
        #     self._generate_airplane_patterns(hand, patterns)

        # 生成顺子
        if hand_size >= 5:
            self._generate_straight_patterns(hand, patterns)
        
        # 生成连对
        if hand_size >= 4:
            self._generate_double_straight_patterns(hand, patterns)

        # 生成三带二
        if hand_size >= 5:
            self._generate_three_with_two_patterns(hand, patterns)
        
        # 生成对子
        self._generate_pair_patterns(hand, patterns)
        
        # 生成单张（优先级最低）
        self._generate_single_patterns(hand, patterns)
        
    def _generate_single_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成单张牌型"""
        # 按点数分组，每个点数只生成一次
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = card  # 只保存一张牌
        
        for point, card in point_cards.items():
            pattern = CardPattern(CardType.SINGLE, [card], card.point)
            patterns.append(pattern)
    
    def _generate_pair_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成对子牌型"""
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = []
            point_cards[card.point].append(card)
        
        for point, cards in point_cards.items():
            if len(cards) >= 2:
                pattern = CardPattern(CardType.PAIR, cards[:2], point)
                patterns.append(pattern)
    
    def _generate_three_with_two_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成三带二牌型"""
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = []
            point_cards[card.point].append(card)
        
        # 找到三同张
        triple_points = [point for point, cards in point_cards.items() if len(cards) >= 3]
        
        # 生成三带二组合
        for triple_point in triple_points:
            triple_cards = point_cards[triple_point][:3]
            # 收集所有其他牌作为带牌候选
            other_cards = []
            for point, cards in point_cards.items():
                if point != triple_point:
                    other_cards.extend(cards)
            
            # 生成所有可能的两牌组合（优化：限制生成数量）
            if len(other_cards) >= 2:
                from itertools import combinations
                # 优化：限制组合数量，避免过多组合导致性能问题
                combo_count = 0
                for combo in combinations(other_cards, 2):
                    pattern = CardPattern(CardType.THREE_WITH_TWO, triple_cards + list(combo), triple_point)
                    patterns.append(pattern)
                    combo_count += 1
                    # 限制每个三同张最多生成20种带牌组合（增加数量以确保能找到合适的组合）

            # 特殊规则：如果只有一张其他牌但这是最后一手牌，也可以打出（三带一）
            elif len(other_cards) == 1:
                pattern = CardPattern(CardType.THREE_WITH_TWO, triple_cards + other_cards, triple_point)
                patterns.append(pattern)
            # 如果没有其他牌，也可以作为三张单独打出（虽然不是标准三带二，但在某些规则下允许）
            elif len(other_cards) == 0:
                pattern = CardPattern(CardType.THREE_WITH_TWO, triple_cards, triple_point)
                patterns.append(pattern)
    
    def _generate_straight_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成顺子牌型"""
        # 按点数分组，每个点数只取一张牌
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = card  # 只保存一张牌
        
        # 获取所有点数并排序
        points = sorted(point_cards.keys())
        
        # 寻找连续的点数序列（至少5张）
        for start in range(len(points)):
            sequence = [points[start]]
            for i in range(start + 1, len(points)):
                # 检查是否连续
                if points[i] == sequence[-1] + 1:
                    sequence.append(points[i])
                else:
                    break
            
            # 如果序列长度至少为5，则生成顺子
            if len(sequence) >= 5:
                # 检查序列中是否包含2（点数15），如果包含则从序列中移除
                if 15 in sequence:
                    sequence = [point for point in sequence if point != 15]
                
                # 如果移除2后序列长度仍然至少为5，则生成所有可能的顺子组合
                if len(sequence) >= 5:
                    # 生成所有可能的顺子组合
                    for i in range(5, len(sequence) + 1):
                        straight_points = sequence[:i]
                        straight_cards = []
                        for point in straight_points:
                            straight_cards.append(point_cards[point])
                        pattern = CardPattern(CardType.STRAIGHT, straight_cards, straight_points[0])
                        patterns.append(pattern)

    def _generate_double_straight_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成连对牌型"""
        # 按点数分组
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = []
            point_cards[card.point].append(card)
        
        # 只保留有对子的点数
        pair_points = [point for point, cards in point_cards.items() if len(cards) >= 2]
        pair_points.sort()
        
        # 寻找连续的对子序列（至少2对）
        for start in range(len(pair_points)):
            sequence = [pair_points[start]]
            for i in range(start + 1, len(pair_points)):
                # 检查是否连续
                if pair_points[i] == sequence[-1] + 1:
                    sequence.append(pair_points[i])
                else:
                    break
            
            # 如果序列长度至少为2，则生成连对
            if len(sequence) >= 2:
                # 生成所有可能的连对组合
                for i in range(2, len(sequence) + 1):
                    straight_points = sequence[:i]
                    straight_cards = []
                    for point in straight_points:
                        straight_cards.extend(point_cards[point][:2])  # 每个点数取两张牌
                    pattern = CardPattern(CardType.DOUBLE_STRAIGHT, straight_cards, straight_points[0])
                    patterns.append(pattern)

    def _generate_bomb_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成炸弹牌型"""
        # 按点数分组
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = []
            point_cards[card.point].append(card)
        
        # 生成普通炸弹（四张同点数）
        for point, cards in point_cards.items():
            if len(cards) >= 4:
                # 四张同点数牌构成炸弹
                pattern = CardPattern(CardType.BOMB, cards[:4], point)
                patterns.append(pattern)
        
        # 生成王炸（三张A）
        ace_cards = point_cards.get(14, [])  # A的点数是14
        if len(ace_cards) >= 3:
            pattern = CardPattern(CardType.BOMB, ace_cards[:3], 14)
            patterns.append(pattern)

    def _generate_airplane_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成飞机牌型（不带翅膀）"""
        # 按点数分组
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = []
            point_cards[card.point].append(card)

        # 只保留三同张
        triples = {point: cards for point, cards in point_cards.items() if len(cards) >= 3}

        # 获取所有三同张点数并排序
        triple_points = sorted(triples.keys())

        # 寻找连续的三同张序列（至少2个）
        for start in range(len(triple_points)):
            sequence = [triple_points[start]]
            for i in range(start + 1, len(triple_points)):
                if triple_points[i] == sequence[-1] + 1:
                    sequence.append(triple_points[i])
                else:
                    break

            # 如果序列长度至少为2，则生成飞机
            if len(sequence) >= 2:
                # 生成所有可能的飞机组合
                for i in range(2, len(sequence) + 1):
                    airplane_points = sequence[:i]
                    airplane_cards = []
                    for point in airplane_points:
                        airplane_cards.extend(triples[point][:3])  # 每个点数选三张牌
                    pattern = CardPattern(CardType.AIRPLANE, airplane_cards, airplane_points[0])
                    patterns.append(pattern)

    def _generate_airplane_with_wings_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成飞机带翅膀牌型"""
        # 按点数分组
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = []
            point_cards[card.point].append(card)

        # 只保留三同张
        triples = {point: cards for point, cards in point_cards.items() if len(cards) >= 3}

        # 获取所有三同张点数并排序
        triple_points = sorted(triples.keys())

        # 寻找连续的三同张序列（至少2个）
        for start in range(len(triple_points)):
            sequence = [triple_points[start]]
            for i in range(start + 1, len(triple_points)):
                if triple_points[i] == sequence[-1] + 1:
                    sequence.append(triple_points[i])
                else:
                    break

            # 如果序列长度至少为2，则生成飞机带翅膀
            if len(sequence) >= 2:
                # 收集所有其他牌作为带牌候选
                other_cards = []
                airplane_points = sequence
                airplane_cards = []
                for point in airplane_points:
                    airplane_cards.extend(triples[point][:3])  # 每个点数选三张牌
                
                for point, cards in point_cards.items():
                    # 不包括飞机主体的点数
                    if point not in airplane_points:
                        other_cards.extend(cards)
                    # 对于飞机主体点数，如果有多于3张牌，则多余的部分可以作为带牌
                    elif len(cards) > 3:
                        other_cards.extend(cards[3:])

                # 生成带翅膀的飞机（带牌数等于飞机主体数）
                wing_count = len(airplane_points)
                if len(other_cards) >= wing_count*2:
                    from itertools import combinations
                    # 限制组合数量，避免过多组合导致性能问题
                    combo_count = 0
                    for combo in combinations(other_cards, wing_count*2):
                        all_cards = airplane_cards + list(combo)
                        pattern = CardPattern(CardType.AIRPLANE_WITH_WINGS, all_cards, airplane_points[0])
                        patterns.append(pattern)
                        combo_count += 1
                        # 限制每个飞机最多生成20种带牌组合


    def _generate_four_with_three_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成四带三牌型"""
        # 按点数分组
        point_cards = {}
        for card in hand:
            if card.point not in point_cards:
                point_cards[card.point] = []
            point_cards[card.point].append(card)
        
        # 查找四张同点数的牌
        quad_points = [point for point, cards in point_cards.items() if len(cards) >= 4]
        
        for quad_point in quad_points:
            quad_cards = point_cards[quad_point][:4]
            # 收集所有其他牌作为带牌候选
            other_cards = []
            for point, cards in point_cards.items():
                if point != quad_point:
                    other_cards.extend(cards)
            
            # 生成所有可能的三牌组合（优化：限制生成数量）
            if len(other_cards) >= 3:
                from itertools import combinations
                # 优化：限制组合数量，避免过多组合导致性能问题
                combo_count = 0
                for combo in combinations(other_cards, 3):
                    pattern = CardPattern(CardType.FOUR_WITH_THREE, quad_cards + list(combo), quad_point)
                    patterns.append(pattern)
                    combo_count += 1
                    # 限制每个四同张最多生成20种带牌组合
                    if combo_count >= 20:
                        break

    def _create_card_pattern(self, cards: List[Card]) -> Optional[CardPattern]:
        """创建牌型对象"""
        return detect_card_type(cards)
