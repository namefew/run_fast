"""
项目配置文件
"""

import os

class Config:
    # 项目根目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 游戏配置
    GAME_CONFIG = {
        "total_cards": 48,  # 总牌数
        "player_count": 2,  # 玩家数量
        "cards_per_player": 16,  # 每个玩家的牌数
        "base_score": 1,    # 底分
    }
    
    # AI配置
    AI_CONFIG = {
        "default_strategy": "advanced",  # 默认AI策略
        "enable_ml_strategy": False,     # 是否启用机器学习策略
    }
    
    # 训练配置
    TRAINING_CONFIG = {
        "episodes": 1000,     # 训练局数
        "save_interval": 100, # 保存间隔
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# 配置字典
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}