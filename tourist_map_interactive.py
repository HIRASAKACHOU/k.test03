import pandas as pd
import pydeck as pdk
import json

# CSVファイルを読み込み（BOM付きUTF-8エンコーディング）
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
latlon_data = pd.read_csv('city_latlon_all.csv', encoding='utf-8')

# 列名を確認して整理
print("City data columns:", city_data.columns.tolist())
print("Latlon data columns:", latlon_data.columns.tolist())

# 地区コードをキーにしてマージ
merged_data = pd.merge(
    city_data,
    latlon_data,
    left_on='地区コード',
    right_on='地区コード',
    how='inner'
)

# 月ごとにHTMLファイルを生成
for month in range(1, 13):
    # 指定月のデータをフィルタリング
    month_data = merged_data[merged_data['月'] == month].copy()
    
    # 人数の最大値を取得（バーの高さのスケーリング用）
    max_visitors = month_data['人数'].max()
    
    # バーの高さを計算（最大50000メートル = 50km）
    month_data['bar_height'] = (month_data['人数'] / max_visitors * 50000).astype(int)
    
    # 色を人数に基づいて設定（赤系のグラデーション）
    month_data['color_value'] = (month_data['人数'] / max_visitors * 255).astype(int)
    month_data['color'] = month_data['color_value'].apply(
        lambda x: [255, max(0, 255-x), 0, 200]  # 赤からオレンジのグラデーション
    )
    
    # PyDeckレイヤーを作成
    layer = pdk.Layer(
        'ColumnLayer',
        data=month_data,
        get_position='[経度, 緯度]',
        get_elevation='bar_height',
        elevation_scale=1,
        radius=5000,  # バーの半径（メートル）
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
    )
    
    # ビューステートを設定（北海道全体が見える位置）
    view_state = pdk.ViewState(
        latitude=43.5,
        longitude=142.5,
        zoom=6,
        pitch=50,
        bearing=0
    )
    
    # ツールチップの設定
    tooltip = {
        "html": "<b>{地区名称}</b><br/>観光者数: {人数:,}人",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white",
            "fontSize": "14px",
            "padding": "10px"
        }
    }
    
    # PyDeckマップを作成
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style='mapbox://styles/mapbox/light-v10'
    )
    
    # HTMLファイルとして保存
    html_filename = f'tourist_map_month_{month:02d}.html'
    deck.to_html(html_filename)
    print(f'{month}月のマップを生成しました: {html_filename}')

# インデックスHTMLを生成（月選択ボタン付き）
index_html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>北海道観光者数マップ 2024</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .button-container {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            padding: 20px;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
        .month-button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 5px;
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            min-width: 80px;
        }
        .month-button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .month-button.active {
            background-color: #e74c3c;
        }
        .map-container {
            width: 100%;
            height: calc(100vh - 200px);
            background-color: white;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        .info {
            text-align: center;
            padding: 10px;
            background-color: white;
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗾 北海道 地区別観光者数マップ 2024</h1>
        <p style="margin-top: 10px; font-size: 14px;">月を選択して観光者数の分布を確認できます</p>
    </div>
    
    <div class="button-container">
"""

# 月のボタンを追加
for month in range(1, 13):
    index_html += f'        <button class="month-button" onclick="loadMonth({month})">{month}月</button>\n'

index_html += """    </div>
    
    <div class="map-container">
        <iframe id="map-frame" src="tourist_map_month_01.html"></iframe>
    </div>
    
    <div class="info">
        <p>🔴 色が濃いほど観光者数が多いことを示します | 📊 バーの高さは相対的な観光者数を表現</p>
        <p>マウスホバーで各地区の詳細情報を表示 | 3D表示で立体的に確認可能</p>
    </div>
    
    <script>
        function loadMonth(month) {
            const monthStr = month.toString().padStart(2, '0');
            const iframe = document.getElementById('map-frame');
            iframe.src = `tourist_map_month_${monthStr}.html`;
            
            // アクティブボタンのスタイルを更新
            const buttons = document.querySelectorAll('.month-button');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        // 初期表示時に1月ボタンをアクティブに
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelector('.month-button').classList.add('active');
        });
    </script>
</body>
</html>
"""

# インデックスHTMLを保存
with open('tourist_map_index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

print('\n✅ すべてのマップを生成しました！')
print('📂 tourist_map_index.html をブラウザで開いてください。')
