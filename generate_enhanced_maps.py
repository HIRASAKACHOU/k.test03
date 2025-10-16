import pandas as pd
import folium
from folium.plugins import MarkerCluster
import json

# CSVファイルを読み込み
print("データを読み込み中...")
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
latlon_data = pd.read_csv('city_latlon_all.csv', encoding='utf-8')

print(f"観光データ: {len(city_data)}行")
print(f"座標データ: {len(latlon_data)}地区")

# カラム名を修正
city_data.columns = ['年', '月', '地区区分', 'データ区分', '都道府県コード', '都道府県名', '地区コード', '地区名称', '人数']

# 地区コードをキーにしてマージ
merged_data = pd.merge(
    city_data,
    latlon_data,
    on='地区コード',
    how='inner'
)

print(f"\nマージ後のデータ: {len(merged_data)}行")

# 月ごとにHTMLファイルを生成
for month in range(1, 13):
    print(f"\n{month}月のマップを生成中...")
    
    # 指定月のデータをフィルタリング
    month_data = merged_data[merged_data['月'] == month].copy()
    
    print(f"  データ数: {len(month_data)}地区")
    
    if len(month_data) == 0:
        print(f"  警告: {month}月のデータがありません")
        continue
    
    # 統計データを計算
    total_visitors = month_data['人数'].sum()
    avg_visitors = month_data['人数'].mean()
    top_5_cities = month_data.nlargest(5, '人数')[['地区名称_y', '都道府県名', '人数']]
    
    # 日本全体が見える位置で地図を作成
    m = folium.Map(
        location=[36.5, 138.0],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # 人数の最大値と最小値を取得
    max_visitors = month_data['人数'].max()
    min_visitors = month_data['人数'].min()
    
    # 都道府県ごとにFeatureGroupを作成
    prefecture_groups = {}
    prefectures_list = sorted(month_data['都道府県名'].unique().tolist())
    
    for pref in prefectures_list:
        prefecture_groups[pref] = folium.FeatureGroup(name=pref)
    
    # 全国表示用のグループ
    all_group = folium.FeatureGroup(name='全国表示', show=True)
    
    # 各地区にマーカーを追加
    import math
    for idx, row in month_data.iterrows():
        # 人数に基づいて円のサイズを決定（実際の人数に比例）
        if row['人数'] > 0:
            # 平方根スケールを使用（面積が人数に比例）
            radius = math.sqrt(row['人数']) / 50  # スケール調整
            radius = max(5, min(radius, 50))  # 5〜50の範囲に制限
        else:
            radius = 5
        
        # 人数に基づいて色を決定
        if max_visitors > min_visitors:
            color_value = (row['人数'] - min_visitors) / (max_visitors - min_visitors)
        else:
            color_value = 0.5
        
        if color_value > 0.7:
            color = '#e74c3c'  # 赤
            fill_color = '#e74c3c'
        elif color_value > 0.4:
            color = '#f39c12'  # オレンジ
            fill_color = '#f39c12'
        else:
            color = '#3498db'  # 青
            fill_color = '#3498db'
        
        # ポップアップの内容
        popup_text = f"""
        <div style="font-family: 'Meiryo', sans-serif; min-width: 220px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid {color}; padding-bottom: 5px;">
                {row['地区名称_y']}
            </h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #ecf0f1;">
                    <td style="padding: 8px 5px; color: #7f8c8d; font-weight: bold;">📍 都道府県</td>
                    <td style="padding: 8px 5px; font-weight: bold;">{row['都道府県名']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ecf0f1; background: #f8f9fa;">
                    <td style="padding: 8px 5px; color: #7f8c8d; font-weight: bold;">👥 観光者数</td>
                    <td style="padding: 8px 5px; font-weight: bold; color: {color}; font-size: 16px;">
                        {row['人数']:,}人
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 5px; color: #7f8c8d; font-weight: bold;">📅 対象月</td>
                    <td style="padding: 8px 5px; font-weight: bold;">{month}月</td>
                </tr>
            </table>
        </div>
        """
        
        # サークルマーカーを作成
        marker = folium.CircleMarker(
            location=[row['緯度'], row['経度']],
            radius=radius,
            popup=folium.Popup(popup_text, max_width=300),
            color=color,
            fillColor=fill_color,
            fillOpacity=0.7,
            weight=2,
            opacity=0.8
        )
        
        # 都道府県グループと全国グループの両方に追加
        marker.add_to(prefecture_groups[row['都道府県名']])
        marker.add_to(all_group)
    
    # 全国グループを地図に追加
    all_group.add_to(m)
    
    # 各都道府県グループを地図に追加（初期は非表示）
    for pref, group in prefecture_groups.items():
        group.add_to(m)
    
    # レイヤーコントロールを追加
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # 統計情報パネルを追加
    stats_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 10px; width: 340px; height: auto;
                background-color: rgba(255, 255, 255, 0.98); z-index:9999; font-size:13px;
                border:3px solid #667eea; border-radius: 12px; padding: 18px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);">
        
        <h3 style="margin: 0 0 12px 0; color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; font-size: 18px;">
            📊 {month}月 統計データ
        </h3>
        
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
            <div style="margin: 8px 0; font-size: 14px;">
                <strong>総観光者数:</strong><br>
                <span style="font-size: 24px; font-weight: bold;">{total_visitors:,}</span>人
            </div>
        </div>
        
        <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 12px;">
            <div style="margin: 6px 0; display: flex; justify-content: space-between;">
                <strong>平均値:</strong> 
                <span style="color: #2c3e50; font-weight: bold;">{avg_visitors:,.0f}人</span>
            </div>
            <div style="margin: 6px 0; display: flex; justify-content: space-between;">
                <strong>対象地区:</strong> 
                <span style="color: #2c3e50; font-weight: bold;">{len(month_data)}地区</span>
            </div>
            <div style="margin: 6px 0; display: flex; justify-content: space-between;">
                <strong>都道府県:</strong> 
                <span style="color: #2c3e50; font-weight: bold;">{len(prefectures_list)}件</span>
            </div>
        </div>
        
        <h4 style="margin: 12px 0 8px 0; color: #2c3e50; font-size: 14px; border-bottom: 2px solid #f39c12; padding-bottom: 5px;">
            🏆 トップ5地区
        </h4>
        <div style="font-size: 12px;">
    '''
    
    medal_colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#3498db', '#95a5a6']
    medal_icons = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    
    for i, (idx, city) in enumerate(top_5_cities.iterrows(), 1):
        stats_html += f'''
            <div style="margin: 6px 0; padding: 8px; background: white; 
                        border-left: 4px solid {medal_colors[i-1]}; border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 3px;">
                    <span style="font-size: 16px; margin-right: 5px;">{medal_icons[i-1]}</span>
                    <strong style="color: #2c3e50;">{city['地区名称_y']}</strong>
                </div>
                <div style="font-size: 11px; color: #7f8c8d; margin-left: 24px;">
                    {city['都道府県名']} | 
                    <span style="color: #e74c3c; font-weight: bold; font-size: 13px;">
                        {city['人数']:,}人
                    </span>
                </div>
            </div>
        '''
    
    stats_html += '''
        </div>
        
        <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #ecf0f1; font-size: 11px; color: #7f8c8d; line-height: 1.6;">
            💡 <strong>凡例:</strong><br>
            🔴 多い（上位30%） 🟠 中程度 🔵 少ない<br>
            📏 <strong>円のサイズ = 観光者数に比例</strong><br>
            🗺️ 右上のレイヤーで都道府県別表示可能
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(stats_html))
    
    # HTMLファイルとして保存
    html_filename = f'tourist_map_month_{month:02d}.html'
    m.save(html_filename)
    print(f"  ✓ {html_filename} を生成しました")

print("\n" + "="*60)
print("✅ すべてのマップを生成しました！")
print("📂 tourist_map_viewer.html をブラウザで開いてください。")
print("\n🎯 新機能:")
print("  1. 円のサイズが観光者数に完全比例")
print("  2. 統計データパネル（総数、平均、トップ5）")
print("  3. 右上のレイヤーコントロールで都道府県別フィルター")
print("  4. タイトルを「日本全国」に変更")
print("="*60)
