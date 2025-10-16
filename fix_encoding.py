import pandas as pd
import json

# 读取CSV，使用utf-8编码（不带BOM）
print("读取city2024.csv...")
with open('city2024.csv', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    
# 打印前几行看看
print("前3行:")
for i, line in enumerate(lines[:3]):
    print(f"行{i}: {repr(line[:100])}")

# 使用pandas读取
df = pd.read_csv('city2024.csv', encoding='utf-8-sig')
print(f"\n列名: {df.columns.tolist()}")
print(f"\n数据形状: {df.shape}")

# 显示第一行数据
print("\n第一行数据:")
print(df.iloc[0])

# 检查都道府県名
print("\n都道府県名的唯一值:")
print(df.iloc[:, 5].unique()[:10])
