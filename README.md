# 🗾 2024年 月別観光者数マップ

インタラクティブな地図上で、2024年の月ごとの地区別観光者数を可視化するWebアプリケーションです。

![Tourist Map Demo](https://img.shields.io/badge/Status-Active-success)
![Cities](https://img.shields.io/badge/Cities-71-blue)
![Prefectures](https://img.shields.io/badge/Prefectures-27-green)

## ✨ 主な機能

### 🎯 統合UIとグラフ（新機能！）
- **1ページで完結**: UIとグラフが同じページに統合され、ページ遷移なしで月を切り替え可能
- **リアルタイム更新**: 月ボタンをクリックすると即座にマップが更新
- **リアルタイム統計**: 選択した月の合計観光者数、最少/最多をリアルタイム表示

### 📊 データ可視化
- **色分け表示**: 観光者数に応じて青→緑→橙→赤の4段階で色分け
- **サイズ表示**: 円の大きさが観光者数に比例
- **詳細情報**: 円にマウスを重ねると地区名と観光者数を表示
- **ポップアップ**: 円をクリックすると詳細情報をポップアップ表示

### 🗺️ 対応地域
- **27都道府県**: 北は北海道から南は沖縄まで
- **71都市**: 主要都市と政令指定都市を含む105地点
- **全国カバー**: 主要観光地を網羅

## 🚀 クイックスタート

### 必要なもの
- Python 3.x
- モダンWebブラウザ

### インストールと実行

```bash
# リポジトリのクローン
git clone https://github.com/HIRASAKACHOU/k.test03.git
cd k.test03

# 仮想環境の作成と有効化
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# パッケージのインストール
pip install -r requirements.txt

# マップの生成
python generate_interactive_map.py

# ブラウザで開く
Start-Process tourist_map_interactive.html  # Windows
# open tourist_map_interactive.html  # Mac
```

## 📱 使い方

1. **tourist_map_interactive.html** をブラウザで開く
2. 上部の **1～12月のボタン** をクリックして月を選択
3. 地図を **ドラッグして移動**、**ホイールでズーム**
4. 円に **マウスを重ねる** と詳細情報が表示されます
5. 円を **クリック** するとポップアップが開きます

## 📊 データについて

- **データ期間**: 2024年1月～12月
- **総データ行数**: 22,452行
- **対象地区**: 1,885地区
- **マップ表示**: 71都市（27都道府県）
- **エンコーディング**: UTF-8 (BOM付き)

## 🎨 カラースキーム

| 色 | 範囲 | 説明 |
|---|---|---|
| 🔵 青 | 0～25% | 観光者数が少ない |
| 🟢 緑 | 25～50% | やや少ない |
| 🟠 橙 | 50～75% | やや多い |
| 🔴 赤 | 75～100% | 観光者数が多い |

## 📂 主なファイル

| ファイル | 説明 |
|---|---|
| **tourist_map_interactive.html** | メインアプリ（統合版） |
| generate_interactive_map.py | マップ生成スクリプト |
| generate_latlon.py | 座標データ生成 |
| city2024.csv | 観光者数データ |
| city_latlon_all.csv | 座標データ（105都市） |

## 🔧 カスタマイズ

### 新しい都市を追加

`generate_latlon.py` を編集：

```python
cities_data = {
    12345: ("新都市名", 緯度, 経度),
}
```

その後、再生成：

```bash
python generate_latlon.py
python generate_interactive_map.py
```

## 🛠️ 技術スタック

- **Python 3.x** - データ処理
- **Pandas** - CSV操作
- **Leaflet.js** - インタラクティブ地図
- **OpenStreetMap** - 地図タイル

## 🔄 更新履歴

### v2.0.0 (2024-10-16) - 統合版 ✨
- UIとグラフを1ページに統合
- 座標データ拡充（66→105都市）
- リアルタイム統計表示
- グラデーションデザイン

### v1.0.0 (2024-10-16) - 初版
- 月別地図12ファイル生成
- 66都市対応

## 📄 ライセンス

教育目的プロジェクト

---

**Made with ❤️ for Data Visualization**

🌐 [GitHubリポジトリ](https://github.com/HIRASAKACHOU/k.test03)
