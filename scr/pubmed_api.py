import requests

def search_pubmed(query, max_results=5):
    """使用 PubMed API 进行 MeSH 术语优化搜索"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    article_ids = data["esearchresult"]["idlist"]
    return article_ids

if __name__ == "__main__":
    query = "COVID-19 treatment"
    print(search_pubmed(query))
