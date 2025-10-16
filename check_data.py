import pandas as pd

# UTF-8-SIGで読み込み
df = pd.read_csv('city2024.csv', encoding='utf-8-sig')

print("実際のカラム名:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\n最初の10行:")
print(df.head(10))

print("\nデータの形状:")
print(f"行数: {len(df)}, 列数: {len(df.columns)}")

# 5番目の列（都道府県名と思われる）のユニークな値
print("\n5番目の列のユニークな値:")
print(df.iloc[:, 5].unique()[:20])
