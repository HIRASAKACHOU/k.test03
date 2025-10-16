import pandas as pd
import folium
from folium.plugins import MarkerCluster
import json

# CSVファイルを読み込み
print("データを読み込み中...")
city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
latlon_data = pd.read_csv('city_latlon_complete.csv', encoding='utf-8')

print(f"観光データ: {len(city_data)}行")
print(f"座標データ: {len(latlon_data)}地区")

# カラム名を修正
city_data.columns = ['年', '月', '地区区分', 'データ区分', '都道府県コード', '都道府県名', '地区コード', '地区名称', '人数']

# 都道府県ごとに観光者数を集計
print("\n都道府県ごとにデータを集約中...")
city_aggregated = city_data.groupby(['年', '月', '都道府県コード']).agg({
    '人数': 'sum'
}).reset_index()

print(f"  集約後: {len(city_aggregated)}行")

# 都道府県の代表坐標を取得（地区コードが都道府県コード*1000のもの）
pref_coords = latlon_data[latlon_data['地区コード'] >= 1000]
pref_coords = pref_coords[pref_coords['地区コード'] % 1000 == 0].copy()
pref_coords['pref_code_calc'] = (pref_coords['地区コード'] / 1000).astype(int)

# 都道府県コードで合併
merged_data = pd.merge(
    city_aggregated,
    pref_coords[['pref_code_calc', '都道府県名', '地区名称', '緯度', '経度']],
    left_on='都道府県コード',
    right_on='pref_code_calc',
    how='inner'
)

print(f"\nマージ後のデータ: {len(merged_data)}行")
print(f"都道府県数: {merged_data['都道府県コード'].nunique()}")

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
    # latlon_dataの都道府県名と地区名称を使用（suffixなし）
    top_5_cities = month_data.nlargest(5, '人数')[['地区名称', '都道府県名', '人数']]
    
    # 日本全体が見える位置で地図を作成
    m = folium.Map(
        location=[36.5, 138.0],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # 人数の最大値と最小値を取得
    max_visitors = month_data['人数'].max()
    min_visitors = month_data['人数'].min()
    
    # 都道府県ごとにFeatureGroupを作成（修正された名前で）
    prefecture_groups = {}
    prefectures_list = sorted(month_data['都道府県名'].unique().tolist())
    
    # 都道府県のマッピング辞書を作成
    prefecture_names_clean = {}
    for pref in prefectures_list:
        # 文字化けした都道府県名を表示用に保持
        prefecture_names_clean[pref] = pref
    
    for pref in prefectures_list:
        # FeatureGroupを作成（show=Falseで初期非表示）
        prefecture_groups[pref] = folium.FeatureGroup(
            name=f'{pref}',
            show=False,
            overlay=True
        )
    
    # 全国表示用のグループ（初期表示）
    all_group = folium.FeatureGroup(name='全国表示', show=True, overlay=True)
    
    # 各地区にマーカーを追加
    import math
    for idx, row in month_data.iterrows():
        # 人数に基づいて円のサイズを決定（平方根スケールで差を強調）
        if row['人数'] > 0:
            # 平方根スケールを使用（面積が人数に比例）
            radius = math.sqrt(row['人数']) / 200  # スケールを調整
            radius = max(4, min(radius, 30))  # 4〜30の範囲
        else:
            radius = 4
        
        # 人数に基づいて色を決定
        if max_visitors > min_visitors:
            color_value = (row['人数'] - min_visitors) / (max_visitors - min_visitors)
        else:
            color_value = 0.5
        
        if color_value > 0.7:
            color = '#e74c3c'
            fill_color = '#e74c3c'
        elif color_value > 0.4:
            color = '#f39c12'
            fill_color = '#f39c12'
        else:
            color = '#3498db'
            fill_color = '#3498db'
        
        # ポップアップの内容（latlon_dataの正しい名前を使用）
        popup_text = f"""
        <div style="font-family: 'Meiryo', sans-serif; min-width: 220px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid {color}; padding-bottom: 5px;">
                {row['地区名称']}
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
        
        # Tooltipの内容（ホバー時に表示）
        tooltip_text = f"""
        <div style="font-family: 'Meiryo', sans-serif;">
            <strong>{row['地区名称']}</strong><br>
            👥 {row['人数']:,}人
        </div>
        """
        
        # サークルマーカーを作成
        marker = folium.CircleMarker(
            location=[row['緯度'], row['経度']],
            radius=radius,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=folium.Tooltip(tooltip_text),  # ホバー時の情報
            color=color,
            fillColor=fill_color,
            fillOpacity=0.7,
            weight=2,
            opacity=0.8
        )
        
        # 都道府県グループと全国グループの両方に追加
        marker.add_to(prefecture_groups[row['都道府県名']])
        
        # 全国グループにも別のマーカーを追加
        marker_all = folium.CircleMarker(
            location=[row['緯度'], row['経度']],
            radius=radius,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=folium.Tooltip(tooltip_text),
            color=color,
            fillColor=fill_color,
            fillOpacity=0.7,
            weight=2,
            opacity=0.8
        )
        marker_all.add_to(all_group)
    
    # 全国グループを地図に追加
    all_group.add_to(m)
    
    # 各都道府県グループを地図に追加
    for pref, group in prefecture_groups.items():
        group.add_to(m)
    
    # レイヤーコントロールを追加（position='topright'）
    folium.LayerControl(
        position='topright',
        collapsed=False,
        autoZIndex=True
    ).add_to(m)
    
    # HTMLファイルを保存（統計パネルは外部に配置するため、ここでは保存しない）
    html_filename = f'tourist_map_month_{month:02d}.html'
    m.save(html_filename)
    
    # 統計データをJSONファイルとして保存
    stats_data = {
        'month': month,
        'total_visitors': int(total_visitors),
        'avg_visitors': float(avg_visitors),
        'num_areas': len(month_data),
        'num_prefectures': len(prefectures_list),
        'top_5': [
            {
                'rank': i + 1,
                'name': row['地区名称'],  # latlon_dataの正しい名前
                'prefecture': row['都道府県名'],  # latlon_dataの正しい都道府県名
                'visitors': int(row['人数'])
            }
            for i, (idx, row) in enumerate(top_5_cities.iterrows())
        ]
    }
    
    with open(f'stats_month_{month:02d}.json', 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ {html_filename} と stats_month_{month:02d}.json を生成しました")

print("\n" + "="*60)
print("✅ すべてのマップと統計データを生成しました！")
print("📂 次に improved_viewer.html を生成します...")
print("="*60)
