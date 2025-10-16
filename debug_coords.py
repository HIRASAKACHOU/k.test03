import pandas as pd

latlon_data = pd.read_csv('city_latlon_complete.csv')

print("所有地区コード:")
print(latlon_data[['地区コード', '都道府県コード', '都道府県名']].head(20))

# 检查都道府県级别的坐标
pref_coords = latlon_data[latlon_data['地区コード'] >= 1000]
print(f"\n地区コード >= 1000的数量: {len(pref_coords)}")

pref_coords_000 = pref_coords[pref_coords['地区コード'] % 1000 == 0]
print(f"地区コード % 1000 == 0的数量: {len(pref_coords_000)}")

print("\n都道府県级别的坐标:")
print(pref_coords_000[['地区コード', '都道府県コード', '都道府県名']])
