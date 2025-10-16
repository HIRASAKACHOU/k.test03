import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import math

# ページ設定
st.set_page_config(
    page_title="日本全国 観光者数インタラクティブマップ 2024",
    page_icon="🗾",
    layout="wide"
)

# タイトル
st.title("🗾 日本全国 観光者数インタラクティブマップ 2024")

# サイドバーで月を選択
month = st.sidebar.selectbox(
    "月を選択",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}月"
)

# データを読み込み
@st.cache_data
def load_data():
    city_data = pd.read_csv('city2024.csv', encoding='utf-8-sig')
    city_data.columns = ['年', '月', '地区区分', 'データ区分', '都道府県コード', '都道府県名', '地区コード', '地区名称', '人数']
    
    latlon_data = pd.read_csv('city_latlon_complete.csv', encoding='utf-8')
    
    # 都道府県ごとに集約
    city_aggregated = city_data.groupby(['年', '月', '都道府県コード']).agg({
        '人数': 'sum'
    }).reset_index()
    
    # 都道府県の代表坐標を取得
    pref_coords = latlon_data[latlon_data['地区コード'] >= 1000]
    pref_coords = pref_coords[pref_coords['地区コード'] % 1000 == 0].copy()
    pref_coords['pref_code_calc'] = (pref_coords['地区コード'] / 1000).astype(int)
    
    # 合併
    merged_data = pd.merge(
        city_aggregated,
        pref_coords[['pref_code_calc', '都道府県名', '地区名称', '緯度', '経度']],
        left_on='都道府県コード',
        right_on='pref_code_calc',
        how='inner'
    )
    
    return merged_data

try:
    data = load_data()
    
    # 選択された月のデータをフィルタリング
    month_data = data[data['月'] == month].copy()
    
    if len(month_data) == 0:
        st.error(f"{month}月のデータがありません")
    else:
        # 統計情報を表示
        col1, col2, col3, col4 = st.columns(4)
        
        total_visitors = month_data['人数'].sum()
        avg_visitors = month_data['人数'].mean()
        num_areas = len(month_data)
        num_prefectures = month_data['都道府県コード'].nunique()
        
        with col1:
            st.metric("総観光者数", f"{total_visitors:,}人")
        with col2:
            st.metric("平均値", f"{int(avg_visitors):,}人")
        with col3:
            st.metric("対象地区", f"{num_areas}地区")
        with col4:
            st.metric("都道府県", f"{num_prefectures}件")
        
        # Top 5を表示
        st.subheader("🏆 トップ5地区")
        top_5 = month_data.nlargest(5, '人数')[['地区名称', '都道府県名', '人数']]
        
        for idx, row in top_5.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{row['地区名称']}** ({row['都道府県名']})")
            with col2:
                st.write(f"**{row['人数']:,}人**")
        
        # 地図を作成
        m = folium.Map(
            location=[36.5, 138.0],
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        max_visitors = month_data['人数'].max()
        min_visitors = month_data['人数'].min()
        
        # マーカーを追加
        for idx, row in month_data.iterrows():
            if row['人数'] > 0:
                radius = math.sqrt(row['人数']) / 200
                radius = max(4, min(radius, 30))
            else:
                radius = 4
            
            if max_visitors > min_visitors:
                color_value = (row['人数'] - min_visitors) / (max_visitors - min_visitors)
            else:
                color_value = 0.5
            
            if color_value > 0.7:
                color = '#e74c3c'
            elif color_value > 0.4:
                color = '#f39c12'
            else:
                color = '#3498db'
            
            popup_text = f"""
            <b>{row['地区名称']}</b><br>
            都道府県: {row['都道府県名']}<br>
            観光者数: {row['人数']:,}人<br>
            対象月: {month}月
            """
            
            folium.CircleMarker(
                location=[row['緯度'], row['経度']],
                radius=radius,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{row['地区名称']}: {row['人数']:,}人",
                color=color,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                opacity=0.8
            ).add_to(m)
        
        # 地図を表示
        st.subheader(f"📍 {month}月の観光者数マップ")
        st_folium(m, width=1400, height=600)

except FileNotFoundError as e:
    st.error(f"データファイルが見つかりません: {e}")
    st.info("必要なファイル: city2024.csv, city_latlon_complete.csv")
except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    st.info("データの読み込みまたは処理中に問題が発生しました。")
