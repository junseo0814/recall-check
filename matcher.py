from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def load_recall_db():
    path = os.path.join('data', 'recall_db.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def make_recall_text(item):
    return f"{item['product_name']} {item['brand']} {item['model']} {item['category']} {item['reason']}"

def match(query_text):
    db = load_recall_db()
    
    recall_texts = [make_recall_text(item) for item in db]
    
    query_vec = model.encode(query_text)
    recall_vecs = model.encode(recall_texts)
    
    scores = np.dot(recall_vecs, query_vec) / (
        np.linalg.norm(recall_vecs, axis=1) * np.linalg.norm(query_vec) + 1e-10
    )
    
    results = []
    for i, item in enumerate(db):
        results.append({
            'recall': item,
            'score': float(scores[i])
        })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
