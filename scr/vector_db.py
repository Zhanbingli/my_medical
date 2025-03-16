import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """计算论文摘要的向量"""
    return model.encode(text, convert_to_numpy=True)

def store_paper_in_faiss(papers):
    """存储论文摘要向量"""
    d = 384
    index = faiss.IndexFlatL2(d)
    
    embeddings = [get_embedding(p['summary']) for p in papers]
    index.add(np.array(embeddings))

    return index

def search_similar_papers(query, index, papers):
    """查询最相关的论文"""
    query_vec = get_embedding(query).reshape(1, -1)
    D, I = index.search(query_vec, k=3)
    return [papers[i] for i in I[0]]

if __name__ == "__main__":
    test_papers = [{"summary": "COVID-19 vaccine study"}]
    index = store_paper_in_faiss(test_papers)
    print(search_similar_papers("vaccine", index, test_papers))
