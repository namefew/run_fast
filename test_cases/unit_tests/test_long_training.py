"""
测试长时间训练是否会出现卡顿问题
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from rl_strategy import train_dqn_agent

def test_long_training():
    """测试长时间训练"""
    print("=== 测试长时间训练 ===")
    print("开始训练10轮...")
    
    try:
        # 训练10轮来测试是否会出现问题
        agent = train_dqn_agent(episodes=10)
        print("训练完成!")
    except Exception as e:
        print(f"训练过程中出现异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_long_training()