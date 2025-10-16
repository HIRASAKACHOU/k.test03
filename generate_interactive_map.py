import pandas as pd
import folium
from folium import plugins
import json

print("データを読み込んでいます...")
# データ読み込み
df_tourist = pd.read_csv('city2024.csv', encoding='utf-8-sig')
df_latlon = pd.read_csv('city_latlon_all.csv', encoding='utf-8-sig')

# 列名を英語に変更（文字化け対策）
df_tourist.columns = ['year', 'month', 'data_type', 'detail_type', 'pref_code', 'pref_name', 
                       'city_code', 'city_name', 'visitors']

print(f"観光データ: {len(df_tourist)}行")
print(f"座標データ: {len(df_latlon)}都市")

# 緯度経度データと結合
df_merged = pd.merge(
    df_tourist,
    df_latlon,
    left_on='city_code',
    right_on='地区コード',
    how='inner'
)

print(f"マージ後: {len(df_merged)}行")
print(f"対象都市数: {df_merged['city_name'].nunique()}")
print(f"対象都道府県数: {df_merged['pref_name'].nunique()}")

# 月ごとのデータを準備
monthly_data = {}
for month in range(1, 13):
    df_month = df_merged[df_merged['month'] == month].copy()
    if len(df_month) > 0:
        monthly_data[month] = df_month.to_dict('records')

print(f"\n月別データを準備しました: {len(monthly_data)}ヶ月分")

# 統合HTMLを生成
html_content = f'''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2024年 観光者数マップ</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .controls {{
            background: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            align-items: center;
        }}
        
        .month-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }}
        
        .month-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        .month-button.active {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
        }}
        
        #map {{
            width: 100%;
            height: calc(100vh - 200px);
        }}
        
        .legend {{
            position: absolute;
            top: 180px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            max-width: 200px;
        }}
        
        .legend h4 {{
            margin-bottom: 10px;
            color: #333;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid #333;
        }}
        
        .stats {{
            background: white;
            padding: 10px 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 20px;
            }}
            
            .month-button {{
                padding: 10px 16px;
                font-size: 14px;
            }}
            
            .legend {{
                font-size: 12px;
                max-width: 150px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🗾 2024年 月別観光者数マップ</h1>
        <p>月を選択して、全国の観光者数分布を確認できます</p>
    </div>
    
    <div class="controls">
        <span style="font-weight: bold; margin-right: 10px;">月を選択:</span>
'''

for month in range(1, 13):
    html_content += f'        <button class="month-button" onclick="showMonth({month})" id="btn-{month}">{month}月</button>\n'

html_content += '''
    </div>
    
    <div class="stats" id="stats">
        月を選択してください
    </div>
    
    <div id="map"></div>
    
    <div class="legend">
        <h4>凡例</h4>
        <div class="legend-item">
            <div class="legend-color" style="background-color: blue;"></div>
            <span>少ない</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: green;"></div>
            <span>やや少ない</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: orange;"></div>
            <span>やや多い</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: red;"></div>
            <span>多い</span>
        </div>
        <hr style="margin: 10px 0;">
        <p style="font-size: 12px; color: #666;">
            円の大きさと色が<br>観光者数を表します
        </p>
    </div>
    
    <script>
        // データ
        const monthlyData = ''' + json.dumps(monthly_data, ensure_ascii=False) + ''';
        
        // 地図初期化
        const map = L.map('map').setView([36.5, 138.0], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        let currentMarkers = [];
        let currentMonth = null;
        
        function getColor(value, minVal, maxVal) {
            if (maxVal === minVal) return 'blue';
            const normalized = (value - minVal) / (maxVal - minVal);
            if (normalized < 0.25) return 'blue';
            if (normalized < 0.5) return 'green';
            if (normalized < 0.75) return 'orange';
            return 'red';
        }
        
        function showMonth(month) {
            // ボタンのスタイル更新
            document.querySelectorAll('.month-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(`btn-${month}`).classList.add('active');
            
            // 既存のマーカーをクリア
            currentMarkers.forEach(marker => map.removeLayer(marker));
            currentMarkers = [];
            currentMonth = month;
            
            const data = monthlyData[month];
            if (!data || data.length === 0) {
                document.getElementById('stats').textContent = `${month}月: データなし`;
                return;
            }
            
            // 観光者数の範囲を計算
            const visitors = data.map(d => d.visitors);
            const minVisitors = Math.min(...visitors);
            const maxVisitors = Math.max(...visitors);
            
            // マーカーを追加
            data.forEach(item => {
                const radius = 2000 + (item.visitors - minVisitors) / (maxVisitors - minVisitors + 1) * 30000;
                const color = getColor(item.visitors, minVisitors, maxVisitors);
                
                const circle = L.circle([item['緯度'], item['経度']], {
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.6,
                    radius: radius
                }).addTo(map);
                
                circle.bindPopup(`
                    <b>${item.city_name}</b><br>
                    ${item.pref_name}<br>
                    観光者数: <b>${item.visitors.toLocaleString()}</b>人
                `);
                
                circle.bindTooltip(`${item.city_name}: ${item.visitors.toLocaleString()}人`, {
                    permanent: false,
                    direction: 'top'
                });
                
                currentMarkers.push(circle);
            });
            
            // 統計情報を更新
            const totalVisitors = visitors.reduce((a, b) => a + b, 0);
            document.getElementById('stats').innerHTML = `
                ${month}月 | データ数: ${data.length}都市 | 
                合計観光者数: ${totalVisitors.toLocaleString()}人 | 
                最少: ${minVisitors.toLocaleString()}人 | 
                最多: ${maxVisitors.toLocaleString()}人
            `;
        }
        
        // 初期表示（1月）
        showMonth(1);
    </script>
</body>
</html>
'''

# HTMLファイルとして保存
with open('tourist_map_interactive.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n✓ tourist_map_interactive.html を生成しました！")
print("このファイルをブラウザで開いて、月を選択してください。")
