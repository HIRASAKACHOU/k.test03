import pandas as pd

df = pd.read_csv('city_latlon_complete.csv')
print(f'坐标文件中的都道府県数: {df["都道府県コード"].nunique()}')
print('\n都道府県コード:')
codes = sorted(df["都道府県コード"].dropna().unique())
print(codes)
print(f'\n总数: {len(codes)}')
