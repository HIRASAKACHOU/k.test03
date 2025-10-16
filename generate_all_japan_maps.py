import pandas as pd
import folium
from folium.plugins import MarkerCluster

# CSVファイルを読み込み
print("データを読み込み中...")
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
latlon_data = pd.read_csv('city_latlon_all.csv', encoding='utf-8')

print(f"観光データ: {len(city_data)}行")
print(f"座標データ: {len(latlon_data)}地区")

# カラム名を取得（文字化けしているため、インデックスで指定）
# 0:年, 1:月, 2:地区区分, 3:データ区分, 4:都道府県コード, 5:都道府県名, 6:地区コード, 7:地区名称, 8:人数
city_data.columns = ['年', '月', '地区区分', 'データ区分', '都道府県コード', '都道府県名', '地区コード', '地区名称', '人数']

print("\nデータの最初の数行:")
print(city_data.head())

# 地区コードをキーにしてマージ
merged_data = pd.merge(
    city_data,
    latlon_data,
    on='地区コード',
    how='inner'
)

print(f"\nマージ後のデータ: {len(merged_data)}行")

# 都道府県別の集計
prefectures = merged_data.groupby('都道府県名')['地区コード'].nunique()
print(f"\n都道府県数: {len(prefectures)}")
print("各都道府県の地区数:")
print(prefectures.head(10))

# 月ごとにHTMLファイルを生成
for month in range(1, 13):
    print(f"\n{month}月のマップを生成中...")
    
    # 指定月のデータをフィルタリング
    month_data = merged_data[merged_data['月'] == month].copy()
    
    print(f"  データ数: {len(month_data)}地区")
    
    if len(month_data) == 0:
        print(f"  警告: {month}月のデータがありません")
        continue
    
    # 日本全体が見える位置で地図を作成
    m = folium.Map(
        location=[36.5, 138.0],  # 日本の中心
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # マーカークラスタを使用
    marker_cluster = MarkerCluster().add_to(m)
    
    # 人数の最大値を取得（円のサイズのスケーリング用）
    max_visitors = month_data['人数'].max()
    min_visitors = month_data['人数'].min()
    
    # 統計データを計算
    total_visitors = month_data['人数'].sum()
    avg_visitors = month_data['人数'].mean()
    top_5_cities = month_data.nlargest(5, '人数')[['地区名称_y', '都道府県名', '人数']]
    
    # 各地区にマーカーを追加
    for idx, row in month_data.iterrows():
        # 人数に基づいて円のサイズを決定（実際の人数に比例、より大きく）
        # 対数スケールを使用してより視覚的に分かりやすく
        import math
        if row['人数'] > 0:
            radius = math.log10(row['人数'] + 1) * 5  # 対数スケールで5〜35程度
        else:
            radius = 5
        
        # 人数に基づいて色を決定
        if max_visitors > min_visitors:
            color_value = (row['人数'] - min_visitors) / (max_visitors - min_visitors)
        else:
            color_value = 0.5
        
        if color_value > 0.7:
            color = 'red'
        elif color_value > 0.4:
            color = 'orange'
        else:
            color = 'blue'
        
        # ポップアップの内容
        popup_text = f"""
        <div style="font-family: sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{row['地区名称_y']}</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 5px; color: #7f8c8d;">都道府県</td>
                    <td style="padding: 5px; font-weight: bold;">{row['都道府県名']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 5px; color: #7f8c8d;">観光者数</td>
                    <td style="padding: 5px; font-weight: bold; color: #e74c3c;">{row['人数']:,}人</td>
                </tr>
                <tr>
                    <td style="padding: 5px; color: #7f8c8d;">月</td>
                    <td style="padding: 5px; font-weight: bold;">{month}月</td>
                </tr>
            </table>
        </div>
        """
        
        # サークルマーカーを追加
        folium.CircleMarker(
            location=[row['緯度'], row['経度']],
            radius=radius,
            popup=folium.Popup(popup_text, max_width=300),
            color=color,
            fillColor=color,
            fillOpacity=0.6,
            weight=2
        ).add_to(marker_cluster)
    
    # 統計情報パネルを追加
    stats_html = f'''
    <div style="position: fixed; 
                top: 80px; left: 10px; width: 320px; height: auto;
                background-color: rgba(255, 255, 255, 0.95); z-index:9999; font-size:13px;
                border:2px solid #667eea; border-radius: 10px; padding: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <h3 style="margin: 0 0 10px 0; color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 8px;">
            📊 {month}月 統計データ
        </h3>
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <div style="margin: 5px 0;">
                <strong>総観光者数:</strong> 
                <span style="color: #e74c3c; font-size: 16px; font-weight: bold;">{total_visitors:,}</span>人
            </div>
            <div style="margin: 5px 0;">
                <strong>平均:</strong> {avg_visitors:,.0f}人/地区
            </div>
            <div style="margin: 5px 0;">
                <strong>対象地区数:</strong> {len(month_data)}地区
            </div>
        </div>
        <h4 style="margin: 10px 0 5px 0; color: #2c3e50; font-size: 13px;">🏆 トップ5地区</h4>
        <div style="font-size: 11px;">
    '''
    
    for i, (idx, city) in enumerate(top_5_cities.iterrows(), 1):
        stats_html += f'''
            <div style="margin: 5px 0; padding: 5px; background: #fff; border-left: 3px solid {"#e74c3c" if i==1 else "#f39c12" if i==2 else "#3498db"}; border-radius: 3px;">
                <strong>{i}位.</strong> {city['地区名称_y']} ({city['都道府県名']})<br>
                <span style="color: #e74c3c; font-weight: bold;">{city['人数']:,}人</span>
            </div>
        '''
    
    stats_html += '''
        </div>
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 11px; color: #7f8c8d;">
            💡 円のサイズ = 観光者数<br>
            🔴 多い 🟠 中程度 🔵 少ない
        </div>
    </div>
    '''
    
    # 都道府県フィルターセレクターを追加
    prefectures_list = sorted(month_data['都道府県名'].unique().tolist())
    filter_html = '''
    <div style="position: fixed; 
                top: 10px; left: 10px; width: 320px; height: auto;
                background-color: rgba(255, 255, 255, 0.95); z-index:9999; font-size:14px;
                border:2px solid #667eea; border-radius: 10px; padding: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <label for="prefecture-filter" style="font-weight: bold; color: #2c3e50; display: block; margin-bottom: 8px;">
            🗺️ 地域フィルター
        </label>
        <select id="prefecture-filter" onchange="filterMarkers()" 
                style="width: 100%; padding: 8px; border: 2px solid #667eea; border-radius: 5px; 
                       font-size: 14px; background: white; cursor: pointer;">
            <option value="all">🌏 全国表示</option>
    '''
    
    for pref in prefectures_list:
        filter_html += f'<option value="{pref}">{pref}</option>\n'
    
    filter_html += '''
        </select>
        <div style="margin-top: 10px; font-size: 12px; color: #7f8c8d;">
            都道府県を選択して絞り込み表示
        </div>
    </div>
    
    <script>
        function filterMarkers() {
            var selectedPref = document.getElementById('prefecture-filter').value;
            var markers = document.querySelectorAll('.leaflet-marker-icon, .leaflet-marker-shadow');
            
            if (selectedPref === 'all') {
                // 全て表示
                markers.forEach(function(marker) {
                    marker.style.display = '';
                });
            } else {
                // フィルタリング（実装の簡略化のため、ページリロードで対応）
                alert('都道府県フィルター機能は次のバージョンで実装予定です。\\n現在は全国表示のみ対応しています。');
                document.getElementById('prefecture-filter').value = 'all';
            }
        }
    </script>
    '''
    
    m.get_root().html.add_child(folium.Element(stats_html))
    m.get_root().html.add_child(folium.Element(filter_html))
    
    # HTMLファイルとして保存
    html_filename = f'tourist_map_month_{month:02d}.html'
    m.save(html_filename)
    print(f"  ✓ {html_filename} を生成しました")

print("\n" + "="*50)
print("✅ すべてのマップを生成しました！")
print("📂 tourist_map_viewer.html をブラウザで開いてください。")
print("="*50)
