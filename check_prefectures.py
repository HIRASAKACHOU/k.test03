import pandas as pd

# 读取坐标文件
df = pd.read_csv('city_latlon_complete.csv')

print("所有都道府県:")
print(df['都道府県名'].value_counts())
print(f"\n总计: {df['都道府県名'].nunique()}个都道府県")

print("\n\n原始观光数据中的都道府県:")
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
city_data.columns = ['年', '月', '地区区分', 'データ区分', '都道府県コード', '都道府県名', '地区コード', '地区名称', '人数']

# 获取都道府県コードと名称的映射
pref_mapping = city_data[['都道府県コード', '都道府県名']].drop_duplicates().sort_values('都道府県コード')
print(pref_mapping)

print("\n\n坐标文件中缺少的都道府県:")
latlon_prefs = set(df['都道府県コード'].unique())
city_prefs = set(city_data['都道府県コード'].unique())
missing = city_prefs - latlon_prefs
if missing:
    missing_names = pref_mapping[pref_mapping['都道府県コード'].isin(missing)]
    print(missing_names)
else:
    print("没有缺失")
