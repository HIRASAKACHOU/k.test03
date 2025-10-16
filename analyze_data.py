import pandas as pd

# Shift_JISでCSVを読み込む
df = pd.read_csv('city2024.csv', encoding='shift_jis')

# データの構造を確認
print("データの列名:")
print(df.columns.tolist())
print("\nデータの最初の5行:")
print(df.head())
print("\nデータの形状:")
print(df.shape)
print("\n地区名のユニーク値（最初の20個）:")
print(df['地区名称'].unique()[:20])
