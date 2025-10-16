import pandas as pd

# 異なるエンコーディングを試す
encodings = ['shift_jis', 'cp932', 'shift_jisx0213', 'utf-8', 'utf-8-sig', 'latin1']

for enc in encodings:
    try:
        print(f"\nTrying encoding: {enc}")
        city_data = pd.read_csv('city2024.csv', encoding=enc)
        print(f"Success! Columns: {city_data.columns.tolist()}")
        print(f"First row: {city_data.iloc[0].to_dict()}")
        break
    except Exception as e:
        print(f"Failed: {type(e).__name__}: {str(e)[:100]}")
