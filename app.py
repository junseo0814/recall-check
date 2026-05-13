
import os
from flask import Flask, render_template, request, jsonify
from matcher import match
from google import genai
import json

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()
gemini = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
def get_llm_explanation(query, top_match):
    recall = top_match['recall']
    score = top_match['score']

    prompt = f"""아래 판매 상품이 리콜 제품과 유사한지 분석해주세요.

[판매 상품]
{query}

[가장 유사한 리콜 제품]
- 제품명: {recall['product_name']}
- 브랜드: {recall['brand']}
- 모델명: {recall['model']}
- 리콜 사유: {recall['reason']}
- 조치사항: {recall['action']}
- 유사도 점수: {score:.2f}

유사도가 0.5 이상이면 위험, 0.3~0.5면 주의, 0.3 미만이면 안전으로 판단하세요.
아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
{{
  "verdict": "위험" 또는 "주의" 또는 "안전",
  "explanation": "2~3문장으로 판단 근거 설명"
}}"""

    response = gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()
    text = text.replace('```json', '').replace('```', '').strip()
    print("Gemini 응답:", text)
    return json.loads(text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def check():
    data = request.json
    query = f"{data.get('product_name', '')} {data.get('brand', '')} {data.get('model', '')} {data.get('category', '')}"
    query = query.strip()

    if not query:
        return jsonify({'error': '상품 정보를 입력해주세요'}), 400

    matches = match(query)
    top3 = matches[:3]
    top1 = matches[0]

    try:
        llm_result = get_llm_explanation(query, top1)
    except Exception as e:
        print("LLM 에러:", e)
        score = top1['score']
        if score >= 0.5:
            verdict = "위험"
            explanation = f"유사도 {score:.2f}로 리콜 제품과 높은 유사성이 감지되었습니다."
        elif score >= 0.3:
            verdict = "주의"
            explanation = f"유사도 {score:.2f}로 리콜 제품과 일부 유사성이 있습니다."
        else:
            verdict = "안전"
            explanation = f"유사도 {score:.2f}로 리콜 제품과 유사성이 낮습니다."
        llm_result = {'verdict': verdict, 'explanation': explanation}

    return jsonify({
        'verdict': llm_result['verdict'],
        'explanation': llm_result['explanation'],
        'top_matches': [
            {
                'product_name': m['recall']['product_name'],
                'brand': m['recall']['brand'],
                'model': m['recall']['model'],
                'reason': m['recall']['reason'],
                'action': m['recall']['action'],
                'recall_date': m['recall']['recall_date'],
                'score': round(m['score'] * 100, 1)
            } for m in top3
        ]
    })

if __name__ == '__main__':
    print("\n✅ RecallCheck 서버 시작!")
    print("👉 브라우저에서 http://localhost:5000 으로 접속하세요\n")
    app.run(debug=True, port=5000)