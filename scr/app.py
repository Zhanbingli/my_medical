import streamlit as st
from pubmed_api import search_pubmed
from gemini_ai import parse_pubmed_article

st.title("🧑‍⚕️ AI 医学助手")

query = st.text_input("请输入查询关键词")
if st.button("🔍 搜索 PubMed"):
    article_ids = search_pubmed(query)
    st.write("找到的论文 ID：", article_ids)

uploaded_file = st.file_uploader("上传论文 PDF 进行解析")
if uploaded_file:
    pdf_text = uploaded_file.read().decode("utf-8")  # 这里你可以用 pdfminer 解析 PDF
    summary = parse_pubmed_article(pdf_text)
    st.write(summary)
