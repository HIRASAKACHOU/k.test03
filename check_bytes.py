
# ファイルの最初の数バイトを確認
with open('city2024.csv', 'rb') as f:
    first_bytes = f.read(100)
    print("First 100 bytes:")
    print(first_bytes)
    print("\nFirst bytes as hex:")
    print(' '.join(f'{b:02x}' for b in first_bytes[:50]))
    
# BOMをチェック
if first_bytes[:3] == b'\xef\xbb\xbf':
    print("\n✓ UTF-8 BOM detected")
elif first_bytes[:2] == b'\xff\xfe':
    print("\n✓ UTF-16 LE BOM detected")
elif first_bytes[:2] == b'\xfe\xff':
    print("\n✓ UTF-16 BE BOM detected")
else:
    print("\n✗ No BOM detected")
