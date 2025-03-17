import faiss
import numpy as np
import os
import pickle
import json
from sentence_transformers import SentenceTransformer
from datetime import datetime

# 使用适合医学文本的模型
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

class MedicalVectorDB:
    """医学论文向量数据库"""
    
    def __init__(self, data_dir='../data'):
        """初始化向量数据库"""
        self.data_dir = data_dir
        self.papers = []
        self.index = None
        self.embedding_dim = 768  # PubMedBERT的维度
        
        # 创建数据目录（如果不存在）
        os.makedirs(data_dir, exist_ok=True)
        
        # 尝试加载现有数据库
        self.load_database()
    
    def get_embedding(self, text):
        """计算文本的向量表示"""
        if not text or text.strip() == "":
            # 处理空文本
            return np.zeros(self.embedding_dim)
        return model.encode(text, convert_to_numpy=True)
    
    def add_papers(self, new_papers):
        """添加新论文到数据库"""
        if not new_papers:
            return False
        
        # 检查是否有重复论文（通过PMID）
        existing_pmids = {paper.get('pmid') for paper in self.papers if 'pmid' in paper}
        unique_papers = [p for p in new_papers if p.get('pmid') not in existing_pmids]
        
        if not unique_papers:
            print("No new unique papers to add.")
            return False
        
        print(f"Adding {len(unique_papers)} new papers to the database.")
        
        # 为每篇论文生成向量
        for paper in unique_papers:
            # 组合标题和摘要以获得更好的表示
            text_for_embedding = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            paper['embedding'] = self.get_embedding(text_for_embedding).tolist()
            paper['added_date'] = datetime.now().isoformat()
            self.papers.append(paper)
        
        # 重建索引
        self._build_index()
        
        # 保存更新后的数据库
        self.save_database()
        return True
    
    def _build_index(self):
        """构建FAISS索引"""
        if not self.papers:
            print("No papers to index.")
            return
        
        # 提取所有论文的向量
        embeddings = [np.array(paper['embedding'], dtype=np.float32) for paper in self.papers]
        embeddings_matrix = np.vstack(embeddings)
        
        # 创建索引
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings_matrix)
        print(f"Built index with {len(self.papers)} papers.")
    
    def search(self, query, k=5):
        """搜索与查询最相关的论文"""
        if not self.index or not self.papers:
            print("Database is empty. No papers to search.")
            return []
        
        # 计算查询的向量表示
        query_vector = self.get_embedding(query).reshape(1, -1)
        
        # 搜索最相似的向量
        distances, indices = self.index.search(query_vector, k=min(k, len(self.papers)))
        
        # 返回结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.papers):  # 确保索引有效
                paper = self.papers[idx].copy()
                paper['score'] = float(distances[0][i])  # 添加相似度分数
                # 移除embedding以减小大小
                if 'embedding' in paper:
                    del paper['embedding']
                results.append(paper)
        
        return results
    
    def filter_search(self, query, filters=None, k=5):
        """带过滤条件的搜索
        
        filters: 字典，包含过滤条件，如 {'pub_date_after': '2022-01-01'}
        """
        # 先获取更多结果，然后应用过滤
        initial_results = self.search(query, k=min(k*3, len(self.papers)))
        
        if not filters:
            return initial_results[:k]
        
        filtered_results = []
        for paper in initial_results:
            # 应用过滤条件
            include = True
            
            # 按发布日期过滤
            if 'pub_date_after' in filters and 'pub_date' in paper:
                try:
                    paper_date = paper['pub_date']
                    filter_date = filters['pub_date_after']
                    if paper_date < filter_date:
                        include = False
                except:
                    pass
            
            # 按作者过滤
            if 'author' in filters and 'authors' in paper:
                if filters['author'].lower() not in paper['authors'].lower():
                    include = False
            
            # 按期刊过滤
            if 'journal' in filters and 'source' in paper:
                if filters['journal'].lower() not in paper['source'].lower():
                    include = False
            
            if include:
                filtered_results.append(paper)
            
            # 如果已经有足够的结果，就停止
            if len(filtered_results) >= k:
                break
        
        return filtered_results[:k]
    
    def save_database(self):
        """保存数据库到文件"""
        try:
            # 保存论文数据（不包括索引）
            papers_file = os.path.join(self.data_dir, 'papers.json')
            with open(papers_file, 'w', encoding='utf-8') as f:
                # 将embedding转换为列表以便JSON序列化
                serializable_papers = []
                for paper in self.papers:
                    paper_copy = paper.copy()
                    if 'embedding' in paper_copy and not isinstance(paper_copy['embedding'], list):
                        paper_copy['embedding'] = paper_copy['embedding'].tolist()
                    serializable_papers.append(paper_copy)
                json.dump(serializable_papers, f, ensure_ascii=False, indent=2)
            
            print(f"Saved {len(self.papers)} papers to {papers_file}")
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def load_database(self):
        """从文件加载数据库"""
        papers_file = os.path.join(self.data_dir, 'papers.json')
        
        if not os.path.exists(papers_file):
            print(f"No existing database found at {papers_file}")
            return False
        
        try:
            with open(papers_file, 'r', encoding='utf-8') as f:
                self.papers = json.load(f)
            
            # 确保所有embedding都是numpy数组
            for paper in self.papers:
                if 'embedding' in paper and isinstance(paper['embedding'], list):
                    paper['embedding'] = np.array(paper['embedding'], dtype=np.float32)
            
            # 重建索引
            self._build_index()
            
            print(f"Loaded {len(self.papers)} papers from {papers_file}")
            return True
        except Exception as e:
            print(f"Error loading database: {e}")
            return False
    
    def clear_database(self):
        """清空数据库"""
        self.papers = []
        self.index = None
        
        # 删除数据文件
        papers_file = os.path.join(self.data_dir, 'papers.json')
        if os.path.exists(papers_file):
            os.remove(papers_file)
        
        print("Database cleared.")
        return True
    
    def get_statistics(self):
        """获取数据库统计信息"""
        if not self.papers:
            return {"total_papers": 0}
        
        # 计算各种统计信息
        journals = {}
        authors_set = set()
        years = {}
        
        for paper in self.papers:
            # 统计期刊
            journal = paper.get('source')
            if journal:
                journals[journal] = journals.get(journal, 0) + 1
            
            # 统计作者
            paper_authors = paper.get('authors', '').split(', ')
            for author in paper_authors:
                if author and author != 'Unknown authors':
                    authors_set.add(author)
            
            # 统计年份
            pub_date = paper.get('pub_date', '')
            if pub_date:
                year = pub_date.split('-')[0] if '-' in pub_date else pub_date
                if year.isdigit():
                    years[year] = years.get(year, 0) + 1
        
        # 排序获取前N个期刊
        top_journals = sorted(journals.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 排序获取年份分布
        years_sorted = sorted(years.items(), key=lambda x: x[0])
        
        return {
            "total_papers": len(self.papers),
            "total_journals": len(journals),
            "total_authors": len(authors_set),
            "top_journals": top_journals,
            "years_distribution": years_sorted
        }

# 测试代码
if __name__ == "__main__":
    db = MedicalVectorDB()
    
    # 测试添加论文
    test_papers = [
        {
            "pmid": "12345",
            "title": "COVID-19 vaccine efficacy study",
            "abstract": "This study investigates the efficacy of various COVID-19 vaccines...",
            "authors": "Smith J, Johnson A",
            "source": "Journal of Immunology",
            "pub_date": "2023-01-15"
        }
    ]
    
    db.add_papers(test_papers)
    
    # 测试搜索
    results = db.search("COVID vaccine effectiveness")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} (Score: {result['score']:.4f})")
        print(f"   Authors: {result['authors']}")
        print(f"   Journal: {result['source']}")
        print(f"   Date: {result['pub_date']}")
        print("-" * 50)
