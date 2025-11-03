"""
测试GPU优化功能
"""

import unittest
import torch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_strategy import DQNAIStrategy
from rl_environment import RLEnvironment


class TestGPUOptimization(unittest.TestCase):
    """测试GPU优化功能"""
    
    def test_device_detection(self):
        """测试设备检测"""
        # 检查设备
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.assertIsInstance(device, torch.device)
        
        # 验证设备字符串格式
        device_str = str(device)
        self.assertIn(device_str, ["cuda", "cpu"])
    
    def test_model_device_placement(self):
        """测试模型设备放置"""
        # 创建一个简单的神经网络进行测试
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = torch.nn.Sequential(
            torch.nn.Linear(100, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 10)
        ).to(device)
        
        # 验证模型参数设备
        for param in model.parameters():
            self.assertEqual(param.device.type, device.type)
    
    def test_rl_components_device(self):
        """测试强化学习组件设备使用"""
        # 创建DQN AI策略
        agent = DQNAIStrategy(player_id=0, state_size=21)
        self.assertIsInstance(agent.device, torch.device)
        
        # 创建环境
        env = RLEnvironment()
        self.assertIsInstance(env.device, torch.device)
        
        # 验证设备一致性
        # agent和env应该使用相同的设备类型
        self.assertEqual(agent.device.type, env.device.type)
    
    def test_state_tensor_device(self):
        """测试状态张量设备"""
        # 创建环境
        env = RLEnvironment()
        state = env.reset()
        
        # 创建DQN AI策略
        agent = DQNAIStrategy(player_id=0, state_size=21)
        
        # 测试状态转换到设备
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(agent.device)
        self.assertEqual(state_tensor.device.type, agent.device.type)


if __name__ == '__main__':
    unittest.main()