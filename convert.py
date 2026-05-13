import pandas as pd
import json

df = pd.read_csv('산업통상부_국가기술표준원_제품안전_국내리콜정보_20230809 (3).csv', encoding='cp949')
df = df.fillna('')

result = []
for i, row in df.iterrows():
    result.append({
        "id": f"R{i+1:04d}",
        "product_name": str(row.get('제품명', '')),
        "brand": str(row.get('브랜드명', '')),
        "model": str(row.get('모델명', '')),
        "category": str(row.get('법정제품분류', '')),
        "recall_date": str(row.get('등록일', '')),
        "reason": str(row.get('위해유형', '')),
        "action": str(row.get('리콜방법', ''))
    })

with open('data/recall_db.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"완료! 총 {len(result)}건 변환됨")