import json

# 读取所有月份的统计数据
all_stats = {}
for month in range(1, 13):
    with open(f'stats_month_{month:02d}.json', 'r', encoding='utf-8') as f:
        all_stats[month] = json.load(f)

# 生成JavaScript对象
js_data = "const STATS_DATA = " + json.dumps(all_stats, ensure_ascii=False, indent=2) + ";"

print("生成的JavaScript数据:")
print(js_data[:500] + "...")
print(f"\n总大小: {len(js_data)} 字符")

# 保存到文件
with open('stats_data.js', 'w', encoding='utf-8') as f:
    f.write(js_data)

print("\n✓ stats_data.js を生成しました")
