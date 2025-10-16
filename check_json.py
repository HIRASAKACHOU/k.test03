import json

with open('stats_month_01.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('总观光者数:', data['total_visitors'])
print('\nTop 5:')
for city in data['top_5']:
    print(f"  {city['rank']}. {city['name']} ({city['prefecture']}) - {city['visitors']:,}人")
