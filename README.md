# 跑得快游戏AI系统

这是一个基于Python的跑得快纸牌游戏AI系统，实现了游戏规则和AI玩家，可以用于训练和测试AI算法。

## 游戏规则

跑得快使用一副牌，去掉大小王、三个2（保留黑桃2）和黑桃A，共48张牌，2个人对战，每人16张牌。游戏的目的是把手中的牌尽快打出去，谁先出完谁赢。

## 功能特性

- 完整的跑得快游戏规则实现
- AI玩家支持（简单策略和高级策略）
- 可扩展的架构，支持添加更多AI策略
- 强化学习AI支持（DQN、PPO等）
- 完整的计分系统
- GPU加速支持

## 项目结构

```
run_fast/
├── .venv/            # 虚拟环境目录
├── docs/             # 文档目录
├── models/           # 训练好的模型目录
├── tests/            # 测试目录
├── cards.py          # 牌类和牌型处理
├── game.py           # 游戏规则引擎
├── player.py         # 玩家类
├── strategy.py       # AI策略模块
├── rl_strategy.py    # 强化学习AI策略
├── rl_environment.py # 强化学习环境
├── train_rl.py       # 强化学习训练脚本
├── test_gpu.py       # GPU支持测试脚本
├── utils.py          # 工具函数
├── config.py         # 配置文件
├── main.py           # 主程序入口
├── run.py            # 启动脚本
├── requirements.txt  # 依赖管理
├── setup.py          # 项目安装配置
└── README.md         # 项目说明
```

## 安装和运行

### 环境要求

- Python 3.8+

### 安装步骤

1. 克隆项目
2. 创建虚拟环境
3. 安装依赖
4. 运行游戏

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (macOS/Linux)
source .venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt

# 安装项目（开发模式）
pip install -e .

# 运行游戏
python run.py
```

或者使用以下命令运行：

```bash
# 直接运行主程序
python main.py

# 使用特定AI类型运行
python main.py --ai1 dqn --ai2 advanced

# 运行AI对战锦标赛
python main.py --tournament
```

## GPU支持

本项目支持GPU加速，当检测到可用的CUDA设备时会自动使用GPU进行计算。

### 安装CUDA支持的PyTorch

```bash
# 安装CUDA版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 测试GPU支持

```bash
# 测试GPU优化
python test_gpu.py
```

如果系统支持CUDA，输出将显示使用GPU设备；否则将使用CPU。

## 模块说明

### cards.py - 牌类和牌型处理模块
- 定义了花色、牌类、牌型枚举
- 实现了牌型识别和比较功能
- 创建了符合规则的48张牌组

### game.py - 游戏规则引擎
- 实现了游戏状态管理和规则执行
- 处理发牌、出牌、跳过等游戏操作
- 包含牌型验证和比较逻辑
- 实现完整的计分系统

### player.py - 玩家类
- 定义了玩家基类和AI玩家类
- 支持人类玩家和AI玩家的扩展

### strategy.py - AI策略模块
- 实现了简单AI和高级AI策略
- 包含出牌决策逻辑
- 为机器学习扩展预留了接口

### rl_strategy.py - 强化学习AI策略
- 实现了基于DQN、PPO等算法的AI策略
- 支持深度强化学习训练
- 自动检测并使用GPU加速

### rl_environment.py - 强化学习环境
- 提供强化学习环境接口
- 实现状态表示、动作空间、奖励函数等
- 支持GPU加速

## 强化学习训练

要训练强化学习AI，可以使用以下命令：

```bash
# 训练DQN模型
python train_rl.py --algorithm dqn --episodes 1000

# 评估训练好的模型
python train_rl.py --algorithm dqn --evaluate
```

## AI策略说明

### 简单策略 (Simple)
基于规则的简单AI，优先出小牌。

### 高级策略 (Advanced)
基于更复杂规则的AI，考虑牌型价值、对手手牌数量等因素。

### DQN策略 (DQN)
基于深度Q网络的强化学习AI。

### 蒙特卡洛树搜索 (MCTS)
基于蒙特卡洛树搜索的AI。

## 开发计划

- [x] 基础游戏规则实现
- [x] 简单AI策略
- [x] 高级AI策略
- [x] 强化学习AI策略
- [x] 完整计分系统
- [x] GPU加速支持
- [ ] 图形用户界面
- [ ] 网络对战支持
- [ ] 更完整的游戏规则支持

## 许可证

MIT License