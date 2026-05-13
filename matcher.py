import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_recall_db():
    path = os.path.join('data', 'recall_db.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def make_recall_text(item):
    return f"{item['product_name']} {item['brand']} {item['model']} {item['category']} {item['reason']}"

def match(query_text):
    db = load_recall_db()
    recall_texts = [make_recall_text(item) for item in db]

    vectorizer = TfidfVectorizer()
    all_texts = [query_text] + recall_texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    query_vec = tfidf_matrix[0]
    recall_vecs = tfidf_matrix[1:]

    scores = cosine_similarity(query_vec, recall_vecs)[0]

    results = []
    for i, item in enumerate(db):
        results.append({
            'recall': item,
            'score': float(scores[i])
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results