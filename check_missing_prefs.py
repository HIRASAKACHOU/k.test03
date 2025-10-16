import pandas as pd

# 都道府県名映射
prefecture_names = {
    1: '北海道', 2: '青森県', 3: '岩手県', 4: '宮城県', 5: '秋田県',
    6: '山形県', 7: '福島県', 8: '茨城県', 9: '栃木県', 10: '群馬県',
    11: '埼玉県', 12: '千葉県', 13: '東京都', 14: '神奈川県', 15: '新潟県',
    16: '富山県', 17: '石川県', 18: '福井県', 19: '山梨県', 20: '長野県',
    21: '岐阜県', 22: '静岡県', 23: '愛知県', 24: '三重県', 25: '滋賀県',
    26: '京都府', 27: '大阪府', 28: '兵庫県', 29: '奈良県', 30: '和歌山県',
    31: '鳥取県', 32: '島根県', 33: '岡山県', 34: '広島県', 35: '山口県',
    36: '徳島県', 37: '香川県', 38: '愛媛県', 39: '高知県', 40: '福岡県',
    41: '佐賀県', 42: '長崎県', 43: '熊本県', 44: '大分県', 45: '宮崎県',
    46: '鹿児島県', 47: '沖縄県'
}

# 读取数据
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
city_data.columns = ['年', '月', '地区区分', 'データ区分', '都道府県コード', '都道府県名', '地区コード', '地区名称', '人数']

latlon_data = pd.read_csv('city_latlon_complete.csv')

# 在观光数据中的都道府県
city_prefs = set(city_data['都道府県コード'].unique())
# 在坐标数据中的都道府県  
latlon_prefs = set(latlon_data['都道府県コード'].unique())

# 缺失的都道府県
missing_prefs = sorted(city_prefs - latlon_prefs)

print(f"观光数据中的都道府県数: {len(city_prefs)}")
print(f"坐标数据中的都道府県数: {len(latlon_prefs)}")
print(f"\n缺失的都道府県 ({len(missing_prefs)}个):")
for code in missing_prefs:
    pref_name = prefecture_names.get(code, f"未知({code})")
    # 获取该都道府県的地区数和人数
    pref_data = city_data[city_data['都道府県コード'] == code]
    num_cities = pref_data['地区コード'].nunique()
    total_visitors = pref_data['人数'].sum()
    print(f"  {code:2d}. {pref_name:8s} - {num_cities}地区, 総観光者数: {total_visitors:,}人")

# 检查是否有大阪府和京都府
print(f"\n京都府(26)在坐标数据中: {'是' if 26 in latlon_prefs else '否'}")
print(f"大阪府(27)在坐标数据中: {'是' if 27 in latlon_prefs else '否'}")

# 显示京都府和大阪府的地区
print("\n京都府の地区:")
kyoto = city_data[city_data['都道府県コード'] == 26]
print(kyoto[['地区コード', '地区名称']].drop_duplicates())

print("\n大阪府の地区:")
osaka = city_data[city_data['都道府県コード'] == 27]
print(osaka[['地区コード', '地区名称']].drop_duplicates())
