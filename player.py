"""
玩家类
"""

from typing import List, Tuple
from cards import Card
from strategy import AIStrategy, SimpleAIStrategy
from game import GameEngine


class Player:
    """玩家基类"""
    
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        self.hand: List[Card] = []
    
    def add_cards(self, cards: List[Card]):
        """添加牌到手牌"""
        self.hand.extend(cards)
        self.hand.sort()
    
    def remove_cards(self, cards: List[Card]):
        """从手牌中移除牌"""
        for card in cards:
            if card in self.hand:
                self.hand.remove(card)


class HumanPlayer(Player):
    """人类玩家"""
    
    def __init__(self, player_id: int, name: str):
        super().__init__(player_id, name)
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """人类玩家选择行动"""
        # 这里可以实现人类玩家的交互逻辑
        # 目前只是简单实现
        print(f"{self.name}的手牌: {self.hand}")
        print("可选的牌型:")
        valid_patterns = engine.get_valid_patterns(self.player_id)
        for i, pattern in enumerate(valid_patterns):
            print(f"{i+1}. {pattern}")
        
        # 简单实现，实际应该有用户界面
        return ("pass", [])


class AIPlayer(Player):
    """AI玩家"""
    
    def __init__(self, player_id: int, name: str, strategy: AIStrategy = None):
        super().__init__(player_id, name)
        self.strategy = strategy if strategy else SimpleAIStrategy(player_id)
    
    def choose_action(self, engine: GameEngine) -> Tuple[str, List[Card]]:
        """AI玩家选择行动"""
        return self.strategy.choose_action(engine)