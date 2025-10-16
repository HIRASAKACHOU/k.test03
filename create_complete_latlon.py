import pandas as pd

# 读取city2024.csv并重命名列
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
city_data.columns = ['年', '月', '地区区分', 'データ区分', '都道府県コード', '都道府県名', '地区コード', '地区名称', '人数']

# 创建地区コード到都道府県コード的映射
code_mapping = city_data[['地区コード', '都道府県コード']].drop_duplicates()

print("地区コード到都道府県コード的映射:")
print(code_mapping.head(20))
print(f"\n映射数量: {len(code_mapping)}")

# 读取坐标文件
latlon = pd.read_csv('city_latlon_all.csv', encoding='utf-8')

# 合并都道府県コード
latlon = latlon.merge(code_mapping, on='地区コード', how='left')

# 都道府県名映射
prefecture_names = {
    1: '北海道',
    2: '青森県',
    3: '岩手県',
    4: '宮城県',
    5: '秋田県',
    6: '山形県',
    7: '福島県',
    8: '茨城県',
    9: '栃木県',
    10: '群馬県',
    11: '埼玉県',
    12: '千葉県',
    13: '東京都',
    14: '神奈川県',
    15: '新潟県',
    16: '富山県',
    17: '石川県',
    18: '福井県',
    19: '山梨県',
    20: '長野県',
    21: '岐阜県',
    22: '静岡県',
    23: '愛知県',
    24: '三重県',
    25: '滋賀県',
    26: '京都府',
    27: '大阪府',
    28: '兵庫県',
    29: '奈良県',
    30: '和歌山県',
    31: '鳥取県',
    32: '島根県',
    33: '岡山県',
    34: '広島県',
    35: '山口県',
    36: '徳島県',
    37: '香川県',
    38: '愛媛県',
    39: '高知県',
    40: '福岡県',
    41: '佐賀県',
    42: '長崎県',
    43: '熊本県',
    44: '大分県',
    45: '宮崎県',
    46: '鹿児島県',
    47: '沖縄県'
}

latlon['都道府県名'] = latlon['都道府県コード'].map(prefecture_names)

# カラムの順序を調整
latlon = latlon[['地区コード', '都道府県コード', '都道府県名', '地区名称', '緯度', '経度']]

print("\n\n更新後のデータ:")
print(latlon.head(15))
print(f"\n合計: {len(latlon)}地区")
print(f"都道府県数: {latlon['都道府県名'].nunique()}")

# 都道府県ごとの地区数を確認
print("\n都道府県ごとの地区数:")
print(latlon['都道府県名'].value_counts().head(10))

# 保存
latlon.to_csv('city_latlon_complete.csv', index=False, encoding='utf-8')
print("\n✓ city_latlon_complete.csv を生成しました")
