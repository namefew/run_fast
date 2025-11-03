import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cards import Card, Suit, detect_card_type, CardType

# 创建测试牌型 [4, 9, 10, 10, 10, 10, 2]
test_cards = [
    Card(Suit.SPADE, '4'),
    Card(Suit.SPADE, '9'),
    Card(Suit.SPADE, '10'),
    Card(Suit.HEART, '10'),
    Card(Suit.DIAMOND, '10'),
    Card(Suit.CLUB, '10'),
    Card(Suit.SPADE, '2')
]

print("测试牌型:")
for card in test_cards:
    print(f"{card} (点数: {card.point})")

# 统计各点数的牌数
points = [card.point for card in test_cards]
point_counts = {}
for point in points:
    point_counts[point] = point_counts.get(point, 0) + 1

print("\n点数统计:")
for point, count in point_counts.items():
    print(f"点数 {point}: {count} 张")

# 手动测试四带三逻辑
print("\n手动测试四带三逻辑:")
values_list = list(point_counts.values())
has_four = 4 in values_list
print(f"是否有四张相同点数的牌: {has_four}")

if has_four:
    # 找到四张相同点数的牌作为主点数
    four_point = [point for point, count in point_counts.items() if count == 4][0]
    print(f"找到四张相同点数的牌，点数为: {four_point}")

print("\n尝试识别牌型...")
pattern = detect_card_type(test_cards)
if pattern:
    print(f"识别成功: {pattern}")
else:
    print("识别失败: 无法识别该牌型")