import pandas as pd

# CSVファイルを読み込み
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')

print("City data columns:")
for i, col in enumerate(city_data.columns):
    print(f"{i}: '{col}'")

print("\nFirst row:")
print(city_data.iloc[0].to_dict())
