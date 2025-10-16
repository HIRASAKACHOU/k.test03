import pandas as pd
import folium
from folium import plugins
import math

# データ読み込み
print("データを読み込んでいます...")
df_tourist = pd.read_csv('city2024.csv', encoding='shift_jis')
df_latlon = pd.read_csv('city_latlon.csv', encoding='utf-8')

# 列名を英語に変更（文字化け対策）
df_tourist.columns = ['year', 'month', 'data_type', 'detail_type', 'pref_code', 'pref_name', 
                       'city_code', 'city_name', 'visitors']

# 緯度経度データと結合
df_merged = pd.merge(
    df_tourist,
    df_latlon,
    left_on='city_code',
    right_on='地区コード',
    how='inner'
)

print(f"データ結合完了: {len(df_merged)}行")
print(f"対象都市数: {df_merged['city_name'].nunique()}")

# 色を観光者数に基づいて設定（青→緑→黄→赤）
def get_color(value, max_val, min_val):
    if max_val == min_val:
        return 'blue'
    normalized = (value - min_val) / (max_val - min_val)
    if normalized < 0.25:
        return 'blue'
    elif normalized < 0.5:
        return 'green'
    elif normalized < 0.75:
        return 'orange'
    else:
        return 'red'

# 月ごとのHTMLファイルを生成
for month in range(1, 13):
    print(f"\n{month}月のデータを処理中...")
    
    # 月でフィルタリング
    df_month = df_merged[df_merged['month'] == month].copy()
    
    if len(df_month) == 0:
        print(f"  警告: {month}月のデータがありません")
        continue
    
    # 観光者数の範囲を取得
    max_visitors = df_month['visitors'].max()
    min_visitors = df_month['visitors'].min()
    
    # 地図を作成（日本の中心）
    m = folium.Map(
        location=[38.0, 140.0],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # 各都市にマーカーを追加
    for idx, row in df_month.iterrows():
        # 円の半径を観光者数に応じて計算（メートル単位）
        radius = 2000 + (row['visitors'] - min_visitors) / (max_visitors - min_visitors + 1) * 30000
        
        # 色を決定
        color = get_color(row['visitors'], max_visitors, min_visitors)
        
        # 円を追加
        folium.Circle(
            location=[row['緯度'], row['経度']],
            radius=radius,
            popup=f"<b>{row['city_name']}</b><br>観光者数: {row['visitors']:,}人",
            tooltip=f"{row['city_name']}: {row['visitors']:,}人",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6
        ).add_to(m)
    
    # 凡例を追加
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
    <h4 style="margin-top:0">{month}月 観光者数</h4>
    <p><i class="fa fa-circle" style="color:blue"></i> 少ない ({min_visitors:,}～)</p>
    <p><i class="fa fa-circle" style="color:green"></i> やや少ない</p>
    <p><i class="fa fa-circle" style="color:orange"></i> やや多い</p>
    <p><i class="fa fa-circle" style="color:red"></i> 多い (～{max_visitors:,})</p>
    <p style="margin-bottom:0; font-size:12px; color:gray;">
    データ数: {len(df_month)}件<br>
    円の大きさ: 観光者数に比例
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # HTMLファイルとして保存
    filename = f'tourist_map_month_{month:02d}.html'
    m.save(filename)
    print(f"  ✓ {filename} を生成しました")
    print(f"    データ数: {len(df_month)}件")
    print(f"    観光者数範囲: {min_visitors:,} ~ {max_visitors:,}人")

# インデックスHTMLファイルを作成
html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2024年 月別観光者数マップ</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .button-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        .month-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .month-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        .month-button:active {
            transform: translateY(0);
        }
        .info {
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
        }
        .info h3 {
            margin-top: 0;
            color: #1976D2;
        }
        .color-legend {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }
        .color-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .color-box {
            width: 30px;
            height: 30px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗾 2024年 月別観光者数マップ</h1>
        
        <div class="button-grid">
"""

for month in range(1, 13):
    html_content += f'            <button class="month-button" onclick="window.open(\'tourist_map_month_{month:02d}.html\', \'_blank\')">{month}月</button>\n'

html_content += """
        </div>
        
        <div class="info">
            <h3>使い方</h3>
            <p>上のボタンをクリックすると、選択した月の観光者数が地図上に表示されます。</p>
            <p>地図上の円の大きさと色が観光者数を表しています。</p>
            <ul>
                <li>円の大きさ：観光者数に比例</li>
                <li>円の色：観光者数の多さを表示（青→緑→黄→赤の順に多い）</li>
                <li>円にマウスを重ねると詳細情報が表示されます</li>
            </ul>
        </div>
        
        <div class="color-legend">
            <div class="color-item">
                <div class="color-box" style="background-color: rgb(0, 0, 255);"></div>
                <span>少ない</span>
            </div>
            <div class="color-item">
                <div class="color-box" style="background-color: rgb(0, 255, 0);"></div>
                <span>やや少ない</span>
            </div>
            <div class="color-item">
                <div class="color-box" style="background-color: rgb(255, 255, 0);"></div>
                <span>やや多い</span>
            </div>
            <div class="color-item">
                <div class="color-box" style="background-color: rgb(255, 0, 0);"></div>
                <span>多い</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n" + "="*60)
print("✓ 全てのファイルの生成が完了しました！")
print("="*60)
print("\nindex.htmlをブラウザで開いて、月を選択してください。")
