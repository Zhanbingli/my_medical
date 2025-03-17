import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_pubmed_details(ids):
    """获取PubMed文章的详细信息"""
    details = []
    for pmid in ids:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                article_data = {}
                
                # 获取PMID
                article_data['pmid'] = pmid
                
                # 获取标题
                title_element = root.find(".//ArticleTitle")
                if title_element is not None and title_element.text:
                    article_data['title'] = title_element.text
                else:
                    article_data['title'] = "No title available"
                
                # 获取摘要
                abstract_texts = root.findall(".//AbstractText")
                if abstract_texts:
                    abstract = " ".join([text.text for text in abstract_texts if text.text])
                    article_data['abstract'] = abstract
                else:
                    article_data['abstract'] = "No abstract available"
                
                # 获取作者
                author_list = root.findall(".//Author")
                authors = []
                for author in author_list:
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None and last_name.text:
                        author_name = last_name.text
                        if fore_name is not None and fore_name.text:
                            author_name = f"{fore_name.text} {author_name}"
                        authors.append(author_name)
                
                article_data['authors'] = ", ".join(authors) if authors else "Unknown authors"
                
                # 获取期刊信息
                journal = root.find(".//Journal/Title")
                if journal is not None and journal.text:
                    article_data['source'] = journal.text
                else:
                    article_data['source'] = "Unknown journal"
                
                # 获取发布日期
                pub_date_elements = root.findall(".//PubDate/*")
                pub_date = {}
                for element in pub_date_elements:
                    if element.tag in ['Year', 'Month', 'Day'] and element.text:
                        pub_date[element.tag.lower()] = element.text
                
                if 'year' in pub_date:
                    date_str = pub_date['year']
                    if 'month' in pub_date:
                        date_str += f"-{pub_date['month']}"
                        if 'day' in pub_date:
                            date_str += f"-{pub_date['day']}"
                    article_data['pub_date'] = date_str
                else:
                    article_data['pub_date'] = "Unknown publication date"
                
                # 获取DOI
                article_id_list = root.findall(".//ArticleId")
                for article_id in article_id_list:
                    if article_id.get("IdType") == "doi" and article_id.text:
                        article_data['doi'] = article_id.text
                        break
                
                details.append(article_data)
            except ET.ParseError as e:
                print(f"Error parsing XML for PMID {pmid}: {e}")
        else:
            print(f"Error fetching details for PMID {pmid}: {response.status_code}")
    
    return details

def search_pubmed(query, max_results=5, days=30):
    """
    搜索PubMed最新研究论文
    
    参数:
    - query: 搜索查询
    - max_results: 返回的最大结果数
    - days: 最近几天的论文 (0表示不限制时间)
    
    返回:
    - 论文详情列表
    """
    # 构建日期限制
    date_filter = ""
    if days > 0:
        date_filter = f" AND {days}[pdat]"
    
    # 构建搜索URL
    search_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={query}{date_filter}"
        f"&retmax={max_results}&retmode=xml&sort=date"
    )
    
    response = requests.get(search_url)
    
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            id_elements = root.findall(".//Id")
            
            if not id_elements:
                print("No PubMed IDs found in the response")
                return []
            
            ids = [id_elem.text for id_elem in id_elements if id_elem.text]
            print(f"Found {len(ids)} PubMed IDs: {', '.join(ids)}")
            
            return fetch_pubmed_details(ids)
        except ET.ParseError as e:
            print(f"Error parsing XML response: {e}")
            return []
    else:
        print(f"Error searching PubMed: {response.status_code}")
        return []

if __name__ == "__main__":
    # 测试搜索功能
    results = search_pubmed("covid vaccine", max_results=3, days=30)
    for result in results:
        print(f"Title: {result.get('title')}")
        print(f"Authors: {result.get('authors')}")
        print(f"Published: {result.get('pub_date')}")
        print(f"Abstract: {result.get('abstract')[:100]}...")
        print("-" * 50)
