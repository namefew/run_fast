import math
from typing import Tuple, List

from cards import Card, CardType, CardPattern, compare_patterns
from game import GameEngine
from strategy import AIStrategy


class HumanStrategy(AIStrategy):
    """基于概率的AI策略"""

    def __init__(self, player_id: int):
        super().__init__(player_id)

    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """基于概率的AI策略 - 改进版本：评估每手牌的价值而不是牌型分组"""
        if engine.is_cover_play():
            valid_patterns = engine.get_valid_patterns(self.player_id)
            if len(valid_patterns) == 0:
                return ("pass", [])

            if len(valid_patterns) == 1:
                return ("play", valid_patterns[0].cards)

            # 获取对手可能的牌
            remaining_cards = self.refine_remaining_cards(engine)
            opponent_possible_patterns = self.generate_all_patterns_from_cards(remaining_cards,  engine)

            # 评估每种出牌选择
            pattern_scores = []
            player_hand = engine.state.players[self.player_id]

            for pattern in valid_patterns:
                # 计算当前出牌的得分
                not_covered_possibility = self.not_covered_possibility(pattern, opponent_possible_patterns, engine)

                # 计算出牌后剩余牌的得分
                remaining_hand = [card for card in player_hand if card not in pattern.cards]
                remaining_score = self._evaluate_remaining_hand(remaining_hand, opponent_possible_patterns, engine)

                # 总得分为当前得分加上剩余牌得分
                total_score =  remaining_score
                pattern_scores.append((pattern, total_score))
            # 选择使得剩余牌得分最高的出牌（尽量过小牌）
            pattern_scores.sort(key=lambda x: x[1], reverse=True)
            best_pattern, score = pattern_scores[0]
            opponent_hand_size = len(engine.state.players[1 - self.player_id])
            if opponent_hand_size==1:
                #如果对手只剩下一手牌，则选择最大的牌
                best_pattern,score = pattern_scores[len(pattern_scores)-1]
            return ("play", best_pattern.cards)

        remaining_cards = self.refine_remaining_cards(engine)
        opponent_possible_patterns = self.generate_all_patterns_from_cards(remaining_cards,  engine)
        all_groups = engine.get_valid_pattern_groups(self.player_id)

        # 找到分数最大的分组
        best_group = None
        max_score = float('-inf')
        
        for group in all_groups:
            score = self.calculate_group_score(group, opponent_possible_patterns, engine)
            if score > max_score:
                max_score = score
                best_group = group
        
        # 如果没有找到有效的分组，返回pass
        if best_group is None:
            return ("pass", [])
        
        # 从最佳分组中选择一个牌型
        chosen_pattern = self.choose_pattern(best_group, opponent_possible_patterns, engine)
        return ("play", chosen_pattern.cards)

    def _evaluate_remaining_hand(self, remaining_hand: List[Card], opponent_possible_patterns: List[CardPattern], engine: GameEngine) -> float:
        """评估剩余手牌的价值"""
        if not remaining_hand:
            return 100  # 没有剩余牌，价值为0
            
        # 生成剩余手牌的所有可能牌型组合分组
        # 创建一个临时的GameEngine来处理剩余手牌
        from game import GameState
        temp_engine = GameEngine()
        temp_engine.state = GameState()

        temp_engine.state.players = [remaining_hand, []]  # 我们只关心玩家0的手牌
        
        # 获取所有可能的出牌分组
        pattern_groups = temp_engine.get_valid_pattern_groups(0)
        
        if not pattern_groups:
            return 0
            
        # 对每个分组计算得分，返回最高得分
        max_score = 0
        for group in pattern_groups:  # 限制检查前5个分组以提高性能
            group_score = self.calculate_group_score(group, opponent_possible_patterns, engine)
            if group_score > max_score:
                max_score = group_score
                
        return max_score

    def refine_remaining_cards(self, engine: GameEngine) -> List[Card]:
        """
        通过之前对手跳过的牌和对方已经出过的牌，来猜测对手可能的手牌
        例如，如果之前出三个8带2张单牌对方跳过，那么remaining_cards中不可能存在超过三个8的牌型，包括炸弹。
        类似的，如果出单Q，对方跳过，那么对方不可能存在大于Q的牌。以此类推。
        这样就可以减少remaining_cards中的数量
        """
        remaining_cards = engine.remaining_cards[:]
        opponent_id = 1 - self.player_id

        point_counts = {}
        for card in remaining_cards:
            point_counts[card.point] = point_counts.get(card.point, 0) + 1

        # 获取对手跳过的回合
        skipped_move_patterns = self.get_opponent_skipped_move_pattern(engine)

        # 分析对手跳过的牌型
        for pattern in skipped_move_patterns:
            # 根据跳过的牌型推测对手手牌
            # 确保pattern存在再处理
            if pattern is not None:
                skipped_point = pattern.main_point
                filtered_cards = []
                if pattern.type == CardType.SINGLE:
                    # 如果对手跳过单牌，说明他可能没有更大的单牌

                    remaining_cards = [c for c in remaining_cards 
                                     if c.point <= skipped_point ]
                    # 移除可能组成炸弹的牌

                    for card in remaining_cards:
                        if point_counts.get(card.point, 0) == 4:  # 添加默认值防止KeyError
                            filtered_cards.append(card)
                            point_counts[card.point] -= 1
                    remaining_cards = [card for card in remaining_cards if card not in filtered_cards]
                elif pattern.type == CardType.PAIR:
                    # 如果对手跳过对子，说明他可能没有更大的对子
                    # 移除可能组成更大对子的牌
                    for card in remaining_cards:
                        # 保留小于等于跳过对子点数的牌，或者可能组成炸弹的牌
                        if card.point <= skipped_point and point_counts.get(card.point, 0) == 4:  # 添加默认值防止KeyError
                            filtered_cards.append(card)
                            point_counts[card.point] -= 1
                        if card.point > skipped_point and point_counts.get(card.point, 0) >= 2:  # 添加默认值防止KeyError
                            filtered_cards.append(card)
                            point_counts[card.point] -= 1
                    remaining_cards = [card for card in remaining_cards if card not in filtered_cards]
                
                elif pattern.type == CardType.THREE_WITH_TWO :
                    # 如果对手跳过三带二，说明他可能没有更大的三同张
                    # 移除可能组成更大三同张的牌
                    for card in remaining_cards:
                        # 移除可能组成更大三同张的牌或炸弹
                        if card.point <= skipped_point and point_counts.get(card.point, 0) == 4:  # 添加默认值防止KeyError
                            filtered_cards.append(card)
                            point_counts[card.point] -= 1
                        if card.point > skipped_point and point_counts.get(card.point, 0) >= 3:  # 添加默认值防止KeyError
                            filtered_cards.append(card)
                            point_counts[card.point] -= 1
                    remaining_cards = [card for card in remaining_cards if card not in filtered_cards]
        

        played_point_counts = self.get_opponent_played_point_counts(engine)

        # 统计对手已出的每种点数的牌数量

        # 如果对手出过某张牌，说明他最多只剩下1张或2张该点数的牌
        filtered_cards = []
        for card in remaining_cards:
            if point_counts.get(card.point, 0) > 3-played_point_counts.get(card.point, 0):  # 添加默认值防止KeyError
                filtered_cards.append(card)
                # 如果对手已出的牌数量多于原始牌库中的牌数量，则将剩余牌中该点数的牌数量设置为对手已出的牌数量
                if card.point in point_counts:  # 检查键是否存在
                    point_counts[card.point] -= 1
        # 根据对手已出的牌，调整剩余牌中每种点数的最大可能数量
        remaining_cards = [card for card in remaining_cards if card not in filtered_cards]

        filtered_cards = []
        # 如果出过三带二的牌型，那么被带的单牌的数量最多剩余1张。
        opponent_moves = [move for move in engine.game_history if move['player'] == opponent_id]
        for move in opponent_moves:
            if move['pattern'] is not None and move['pattern'].type == CardType.THREE_WITH_TWO:
                carried_cards = [card for card in move['pattern'].cards if card.point != move['pattern'].main_point]
                for c in carried_cards:
                    for card in remaining_cards:
                        if card.point == c.point and point_counts.get(card.point, 0) > 1:  # 添加默认值防止KeyError
                            filtered_cards.append(card)
                            if card.point in point_counts:  # 检查键是否存在
                                point_counts[card.point] -= 1
        remaining_cards = [card for card in remaining_cards if card not in filtered_cards]

        return remaining_cards

    def get_opponent_skipped_move_pattern(self, engine):
        '''
        获取对手跳过的手牌
        :param engine:
        :param opponent_id:
        :return:
        '''
        opponent_id = 1 - self.player_id
        skipped_moves = []
        for i in range(len(engine.game_history) - 1):
            move = engine.game_history[i]
            next_move = engine.game_history[i + 1] if i + 1 < len(engine.game_history) else None
            # 如果当前玩家出牌，下一个玩家跳过，说明下一个玩家无法管住当前玩家的牌
            if move['player'] != opponent_id and next_move and next_move['player'] == opponent_id and not next_move[
                'cards']:
                skipped_moves.append(move['pattern'])
        return skipped_moves

    def get_opponent_played_point_counts(self, engine: GameEngine):
        opponent_id = 1 - self.player_id
        opponent_moves = [move for move in engine.game_history if move['player'] == opponent_id]
        opponent_played_cards = []
        for move in opponent_moves:
            opponent_played_cards.extend(move['cards'])
        played_point_counts = {}
        for card in opponent_played_cards:
            played_point_counts[card.point] = played_point_counts.get(card.point, 0) + 1
        return played_point_counts

    def generate_all_patterns_from_cards(self, cards: List[Card], engine:GameEngine):
        """基于给定牌生成所有可能的牌型"""
        patterns = []
        if len(cards) == 0:
            return patterns
        # 生成各种牌型
        engine._generate_single_patterns(cards, patterns)
        engine._generate_pair_patterns(cards, patterns)
        engine._generate_bomb_patterns(cards, patterns)
        engine._generate_straight_patterns(cards, patterns)
        engine._generate_double_straight_patterns(cards, patterns)
        # engine._generate_airplane_patterns(cards, patterns)
        self._generate_three_with_two_patterns(cards, patterns) #不带牌
        self._generate_airplane_with_wings_patterns(cards, patterns) #不带牌
        return  patterns

    def _generate_three_with_two_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成三带二牌型 这里不带牌"""
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
            pattern = CardPattern(CardType.THREE_WITH_TWO, triple_cards , triple_point)
            patterns.append(pattern)

    def _generate_airplane_with_wings_patterns(self, hand: List[Card], patterns: List[CardPattern]):
        """生成飞机带翅膀牌型  这里不带翅膀"""
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
                for i in range(2, len(sequence) + 1):
                    straight_points = sequence[:i]
                    straight_cards = []
                    for point in straight_points:
                        straight_cards.extend(point_cards[point][:3])  # 每个点数取两张牌
                    pattern = CardPattern(CardType.AIRPLANE_WITH_WINGS, straight_cards, straight_points[0])
                    patterns.append(pattern)

    def calculate_group_score(self, group:List[CardPattern], opponent_possible_patterns: List[CardPattern], engine: GameEngine):
        opponent_hand_size = len(engine.state.players[1 - self.player_id])
        #把group中按类型分组
        grouped_patterns = self.group_patterns_by_type(group)
        total_score = 0
        for type, patterns in grouped_patterns.items():
            score = 0
            for pattern in patterns:
                if opponent_hand_size<pattern.card_count and (type==CardType.PAIR or type==CardType.STRAIGHT or type==CardType.DOUBLE_STRAIGHT or type==CardType.AIRPLANE):
                    not_covered_possibility = 1
                else:
                    not_covered_possibility = self.not_covered_possibility(pattern, opponent_possible_patterns, engine)
                    if opponent_hand_size<pattern.card_count:
                        not_covered_possibility = min(1,not_covered_possibility*10)
                score += not_covered_possibility * pattern.card_count
            if type==CardType.BOMB and len(grouped_patterns)>1:
                score = score*5
            total_score += score
        return total_score

    def not_covered_possibility(self, pattern: CardPattern,opponent_possible_patterns: List[CardPattern], engine):
        """
        无法被管住的概率
        """
        opponent_hand_size = len(engine.state.players[1 - self.player_id])
        if pattern.card_count>opponent_hand_size and pattern.type in [CardType.BOMB, CardType.PAIR, CardType.STRAIGHT, CardType.DOUBLE_STRAIGHT, CardType.AIRPLANE] \
                or pattern.type==CardType.AIRPLANE_WITH_WINGS and pattern.card_count/5*3>opponent_hand_size\
                or pattern.type==CardType.THREE_WITH_TWO and pattern.card_count/5*3>opponent_hand_size:
            return 1
        skipped_move_patterns = self.get_opponent_skipped_move_pattern(engine)
        for skip_pattern in skipped_move_patterns:
            if pattern==skip_pattern or compare_patterns(pattern,skip_pattern):
                return 1
        maybe_covered = [p for p in opponent_possible_patterns if compare_patterns(p, pattern)]
        not_covered_possibility = 1
        if len(maybe_covered) == 0:
            return 1
        else:
            for maybe_covered_pattern in maybe_covered:
                possibility = self.possibility(maybe_covered_pattern, engine)
                # 添加保护措施防止数值溢出
                if possibility < 0:
                    possibility = 0
                elif possibility > 1:
                    possibility = 1
                not_covered_possibility *= (1 - possibility)
                # 添加保护措施防止数值异常
                if not_covered_possibility < 0:
                    not_covered_possibility = 0
                elif not_covered_possibility > 1:
                    not_covered_possibility = 1
        return not_covered_possibility

    def group_patterns_by_type(self, group:List[CardPattern]):
        grouped_patterns = {}
        for pattern in group:
            if pattern.type not in grouped_patterns:
                grouped_patterns[pattern.type] = []
            grouped_patterns[pattern.type].append(pattern)
        return grouped_patterns

    def possibility(self, maybe_covered_pattern, engine):
        if maybe_covered_pattern.type == CardType.BOMB :
            if maybe_covered_pattern.main_point != 14:
                # 炸弹 ,四张牌都分到了对家的概率是1/2 * 1/2 * 1/2 * 1/2
                return 0.0625 #math.comb(4,4)/math.pow(2,4)
            else:
                # A的炸弹 3张A都分到了对家的概率是1/2 * 1/2 * 1/2
                return 0.125 #math.comb(3,3)/math.pow(2,3)
        elif maybe_covered_pattern.type == CardType.THREE_WITH_TWO:
            cards = engine.state.players[self.player_id]
            cnt = len([c for c in cards if c.point==maybe_covered_pattern.main_point])
            if cnt==0:
                return 0.25 #math.comb(4,3)/math.pow(2,4)
            else:# cnt只可能可能等于1
                return 0.125  #math.comb(3,3)/math.pow(2,3)
        elif maybe_covered_pattern.type == CardType.AIRPLANE or maybe_covered_pattern.type == CardType.AIRPLANE_WITH_WINGS:
            # 飞机
            result = 1.0
            three_count = int(maybe_covered_pattern.card_count / 3)
            for i in range(three_count):
                point0 = maybe_covered_pattern.main_point+i
                cnt0 = len([c for c in engine.state.players[self.player_id] if c.point==point0])
                if cnt0==0:
                    result *= 0.25
                elif cnt0==1:
                    result *= 0.125
                # 添加保护措施防止数值下溢
                if result < 1e-10:
                    result = 1e-10
            return result
        elif maybe_covered_pattern.type == CardType.PAIR:
            cards = engine.state.players[self.player_id]
            cnt = len([c for c in cards if c.point == maybe_covered_pattern.main_point])
            if cnt==0:
                return 0.6875  #(math.comb(4,2)+math.comb(4,3)+math.comb(4,4))/math.pow(2,4)
            elif cnt==1:
                return 0.5 #(math.comb(3,2)+math.comb(3,3))/math.pow(2,3)
            else:
                return 0.25 #(math.comb(2,2))/math.pow(2,2)
        elif maybe_covered_pattern.type == CardType.DOUBLE_STRAIGHT:
            # 连对
            result = 1.0
            pair_count = int(maybe_covered_pattern.card_count/2)
            for i in range(pair_count):
                point0 = maybe_covered_pattern.main_point+i
                cnt0 = len([c for c in engine.state.players[self.player_id] if c.point==point0])
                if cnt0==0:
                    result *= 0.6875
                elif cnt0==1:
                    result *= 0.5
                else:
                    result *= 0.25
                # 添加保护措施防止数值下溢
                if result < 1e-10:
                    result = 1e-10
            return result
        elif maybe_covered_pattern.type == CardType.SINGLE:
            cnt = len([c for c in engine.state.players[self.player_id] if c.point == maybe_covered_pattern.main_point])
            if maybe_covered_pattern.main_point==14:
                return 1-math.pow(0.5,3-cnt)
            elif maybe_covered_pattern.main_point==15:
                return 1-math.pow(0.5,1-cnt)
            return 1-math.pow(0.5,4-cnt)
        elif maybe_covered_pattern.type == CardType.STRAIGHT:
            # 顺子
            result = 1.0
            for i in range(maybe_covered_pattern.card_count):
                point0 = maybe_covered_pattern.main_point+i
                cnt0 = len([c for c in engine.state.players[self.player_id] if c.point==point0])
                if point0!=14:
                    result *= 1-math.pow(0.5,4-cnt0)
                elif point0==14:
                    result *= 1-math.pow(0.5,3-cnt0)
                # 添加保护措施防止数值下溢
                if result < 1e-10:
                    result = 1e-10
            return result

    def choose_pattern(self, best_pattern_group:List[CardPattern], opponent_possible_patterns:List[CardPattern], engine):

        if len(best_pattern_group)==1:
            return best_pattern_group[0]
        best_pattern_group.sort(key=lambda x:x.card_count,reverse=True)

        grouped_patterns = self.group_patterns_by_type(best_pattern_group)
        pattern_big_rate = {}
        for type, patterns in grouped_patterns.items():
            for pattern in patterns:
                not_covered_possibility = self.not_covered_possibility(pattern, opponent_possible_patterns,engine)
                pattern_big_rate[pattern]=not_covered_possibility
        bigest_count = sum([1 for pattern in best_pattern_group if pattern_big_rate[pattern]==1])

        # 如果只有一种牌型对手可能能管住 优先出最大的牌(这样可以连续出牌，最后赢得比赛）
        if bigest_count >= len(best_pattern_group)-1:
            for pattern in best_pattern_group:
                if pattern_big_rate[pattern] == 1:
                    return pattern

        # 如果对方只剩下一张牌，尽量出最大的牌
        opponent_hand_size = len(engine.state.players[1 - self.player_id])
        if opponent_hand_size==1:
            return max(pattern_big_rate, key=pattern_big_rate.get)

        type_counts = {}
        type_big_count = {}
        for pattern in best_pattern_group:
            if pattern.type not in type_counts:
                type_counts[pattern.type] = 0
            if pattern.type not in type_big_count:
                type_big_count[pattern.type] = 0
            type_counts[pattern.type] += 1
            if pattern_big_rate[pattern] == 1:
                type_big_count[pattern.type] += 1

        # 如果正好有3手牌且其中一个是炸弹,返回第2大的牌
        if len(best_pattern_group) == 3 and type_counts.get(CardType.BOMB, 0) >= 1:
            # 按照被管住的概率从大到小排序
            sorted_patterns = sorted(best_pattern_group, key=lambda p: pattern_big_rate[p], reverse=True)
            return sorted_patterns[1]

        #找出有2手以上最大牌的牌型
        most_big_type = max(type_big_count, key=type_big_count.get)
        if type_counts[most_big_type] > 1:
            if most_big_type==CardType.STRAIGHT:
                #同花顺牌型时，如果数量一致，先出小排，再出大牌；如果数量不一致，先出大牌，再出小牌
                # 检查所有顺子的长度是否一致
                matching_patterns = [pattern for pattern in best_pattern_group if
                                     pattern.type == most_big_type]
                lengths = [pattern.card_count for pattern in matching_patterns]
                if len(set(lengths)) == 1:  # 所有顺子长度相同
                    # 先出小牌（按起始点数排序，返回最小的）
                    return min(matching_patterns, key=lambda p: p.main_point)
                else:  # 顺子长度不一致
                    # 先出大牌（按起始点数排序，返回最大的）
                    return max(matching_patterns, key=lambda p: p.main_point)
            # 如果某种类型的牌有最大牌，且还有小牌，则返回该类型的牌型中的最小的一个 然后过牌，最后用最大牌打回来。
            matching_patterns = [pattern for pattern in best_pattern_group if pattern.type == most_big_type]
            # 返回最小的牌型（按main_point排序）
            return min(matching_patterns, key=lambda p: p.main_point)


        maybe_bigest_count = sum([1 for pattern in best_pattern_group if pattern_big_rate[pattern]>=max(opponent_hand_size/16,0.8)])
        if maybe_bigest_count>=len(best_pattern_group)-1:
            for pattern in best_pattern_group:
                if pattern_big_rate[pattern]>=max(opponent_hand_size/16,0.8):
                    if pattern.type != CardType.BOMB:
                        return pattern

        # 如果没有牌是最大的，尽量先出得分最高的牌型中的 小牌
        #TODO
        # 默认牌数最多的牌先出
        if best_pattern_group[0].type == CardType.BOMB and len(best_pattern_group) > 1:
            return best_pattern_group[1]

        # 如果牌型数量超过5且数量最多的牌的主牌是K或A,则出第二手牌
        if len(best_pattern_group)>5 and best_pattern_group[0].main_point>12:
            return best_pattern_group[1]

        return best_pattern_group[0]