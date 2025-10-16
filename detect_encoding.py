import chardet

# ファイルの最初の数千バイトを読み取ってエンコーディングを検出
with open('city2024.csv', 'rb') as f:
    raw_data = f.read(10000)
    result = chardet.detect(raw_data)
    print(f"Detected encoding: {result}")
    
# 検出されたエンコーディングで読み込み
import pandas as pd
detected_encoding = result['encoding']
print(f"\nTrying to read with {detected_encoding}")

try:
    df = pd.read_csv('city2024.csv', encoding=detected_encoding)
    print(f"Success! Columns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
