import streamlit as st
import time
from pubmed_api import search_pubmed
from gemini_ai import MedicalAssistant
from vector_db import MedicalVectorDB

# 设置页面配置
st.set_page_config(
    page_title="医学AI助手",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化组件
@st.cache_resource
def load_assistant():
    return MedicalAssistant()

@st.cache_resource
def load_vector_db():
    return MedicalVectorDB()

# 加载组件
assistant = load_assistant()
vector_db = load_vector_db()

# 侧边栏
with st.sidebar:
    st.title("医学AI助手")
    st.markdown("基于Gemini API和PubMed论文检索的专业医学助手")
    
    # 模式选择
    st.subheader("选择模式")
    mode = st.radio(
        "请选择使用模式:",
        ["论文检索与分析", "医学问答", "患者教育材料生成", "数据库统计"]
    )
    
    # 高级选项
    st.subheader("高级选项")
    if mode == "论文检索与分析":
        max_results = st.slider("最大结果数", min_value=1, max_value=20, value=5)
        days_filter = st.slider("最近几天的论文", min_value=0, max_value=365, value=30, 
                              help="0表示不限制时间")
        
        st.markdown("---")
        if st.button("清除对话历史"):
            assistant.clear_history()
            st.success("对话历史已清除")
    
    # 数据库管理
    if mode == "数据库统计":
        st.subheader("数据库管理")
        if st.button("清空数据库"):
            if vector_db.clear_database():
                st.success("数据库已清空")
            else:
                st.error("清空数据库失败")

# 主界面
st.title("🏥 专业医学AI助手")

# 论文检索与分析模式
if mode == "论文检索与分析":
    st.subheader("📚 论文检索与分析")
    
    # 创建两列布局
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # 输入框，用于接受用户查询
        query = st.text_input('输入医学研究关键词:', placeholder='例如: COVID-19 treatment')
        
        # 按钮，用于触发搜索
        search_clicked = st.button('搜索PubMed最新研究')
        
        if search_clicked and query:
            with st.spinner("正在搜索PubMed..."):
                # 获取PubMed文献详细信息
                results = search_pubmed(query, max_results=max_results, days=days_filter)
                
                # 保存到向量数据库
                if results:
                    vector_db.add_papers(results)
                    
                    st.session_state.current_papers = results
                    st.success(f"找到 {len(results)} 篇相关论文")
                else:
                    st.warning("未找到相关论文，请尝试其他关键词")
    
    # 显示搜索结果
    if 'current_papers' in st.session_state and st.session_state.current_papers:
        with col2:
            st.subheader("论文分析选项")
            analysis_type = st.radio(
                "选择分析类型:",
                ["单篇论文详细分析", "多篇论文综合分析"]
            )
            
            if analysis_type == "单篇论文详细分析":
                paper_titles = [f"{i+1}. {p.get('title', 'No title')}" 
                              for i, p in enumerate(st.session_state.current_papers)]
                selected_paper_idx = st.selectbox("选择要分析的论文:", paper_titles)
                
                if st.button("分析所选论文"):
                    # 获取选中的论文索引
                    idx = int(selected_paper_idx.split('.')[0]) - 1
                    paper = st.session_state.current_papers[idx]
                    
                    with st.spinner("AI正在分析论文..."):
                        analysis = assistant.parse_pubmed_article(paper)
                        st.session_state.current_analysis = analysis
            
            elif analysis_type == "多篇论文综合分析":
                if st.button("综合分析所有论文"):
                    with st.spinner("AI正在综合分析多篇论文..."):
                        analysis = assistant.analyze_multiple_papers(st.session_state.current_papers)
                        st.session_state.current_analysis = analysis
        
        # 显示论文列表
        st.subheader("搜索结果")
        for i, article in enumerate(st.session_state.current_papers):
            with st.expander(f"{i+1}. {article.get('title', 'No title')}"):
                st.markdown(f"**作者:** {article.get('authors', 'Unknown authors')}")
                st.markdown(f"**期刊:** {article.get('source', 'No journal information')}")
                st.markdown(f"**发布日期:** {article.get('pub_date', 'Unknown date')}")
                st.markdown(f"**摘要:** {article.get('abstract', 'No abstract available.')}")
                if 'pmid' in article:
                    st.markdown(f"[在PubMed上查看](https://pubmed.ncbi.nlm.nih.gov/{article.get('pmid')})")
                if 'doi' in article:
                    st.markdown(f"[DOI链接](https://doi.org/{article.get('doi')})")
        
        # 显示分析结果
        if 'current_analysis' in st.session_state:
            st.subheader("AI分析结果")
            st.markdown(st.session_state.current_analysis)

# 医学问答模式
elif mode == "医学问答":
    st.subheader("💬 医学问答")
    
    # 初始化聊天历史
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 使用相关论文作为上下文
    use_papers = st.checkbox("使用向量数据库中的相关论文作为回答依据")
    
    # 聊天输入
    if prompt := st.chat_input("输入您的医学问题..."):
        # 添加用户消息到聊天历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 显示助手消息
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            with st.spinner("AI思考中..."):
                context_papers = []
                
                # 如果选择使用相关论文
                if use_papers:
                    # 从向量数据库中检索相关论文
                    context_papers = vector_db.search(prompt, k=3)
                    
                    if context_papers:
                        message_placeholder.markdown("*正在查询相关医学文献...*")
                        time.sleep(1)
                
                # 生成回答
                response = assistant.answer_medical_question(prompt, context_papers)
                
                # 显示回答
                message_placeholder.markdown(response)
        
        # 添加助手消息到聊天历史
        st.session_state.messages.append({"role": "assistant", "content": response})

# 患者教育材料生成模式
elif mode == "患者教育材料生成":
    st.subheader("📋 患者教育材料生成")
    
    topic = st.text_input("输入医学主题:", placeholder="例如: 糖尿病自我管理, 高血压饮食控制")
    
    if st.button("生成教育材料") and topic:
        with st.spinner("正在生成患者教育材料..."):
            education_material = assistant.generate_patient_education(topic)
            st.markdown(education_material)
            
            # 提供下载选项
            st.download_button(
                label="下载为PDF",
                data=education_material,
                file_name=f"{topic}_患者教育材料.txt",
                mime="text/plain"
            )

# 数据库统计模式
elif mode == "数据库统计":
    st.subheader("📊 数据库统计")
    
    stats = vector_db.get_statistics()
    
    # 显示基本统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("论文总数", stats.get("total_papers", 0))
    with col2:
        st.metric("期刊数量", stats.get("total_journals", 0))
    with col3:
        st.metric("作者数量", stats.get("total_authors", 0))
    
    # 显示期刊分布
    if "top_journals" in stats and stats["top_journals"]:
        st.subheader("热门期刊")
        journal_data = {j[0]: j[1] for j in stats["top_journals"]}
        st.bar_chart(journal_data)
    
    # 显示年份分布
    if "years_distribution" in stats and stats["years_distribution"]:
        st.subheader("论文年份分布")
        years_data = {y[0]: y[1] for y in stats["years_distribution"]}
        st.line_chart(years_data)
    
    # 添加搜索功能
    st.subheader("数据库搜索")
    search_query = st.text_input("搜索数据库中的论文:", placeholder="输入关键词...")
    
    if st.button("搜索") and search_query:
        results = vector_db.search(search_query, k=10)
        
        if results:
            st.success(f"找到 {len(results)} 篇相关论文")
            
            for i, result in enumerate(results, 1):
                with st.expander(f"{i}. {result.get('title', 'No title')} (相关度: {result.get('score', 0):.4f})"):
                    st.markdown(f"**作者:** {result.get('authors', 'Unknown authors')}")
                    st.markdown(f"**期刊:** {result.get('source', 'No journal information')}")
                    st.markdown(f"**发布日期:** {result.get('pub_date', 'Unknown date')}")
                    st.markdown(f"**摘要:** {result.get('abstract', 'No abstract available.')}")
        else:
            st.warning("未找到相关论文")

# 页脚
st.markdown("---")
st.markdown("© 2025 医学AI助手 | 基于Gemini API和PubMed数据")
