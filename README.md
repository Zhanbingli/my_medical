# 医学AI助手 (Medical AI Assistant)

基于Gemini API和PubMed最新研究论文检索的专业型医学AI助手。本项目结合了Google的Gemini大语言模型和PubMed医学文献数据库，为医疗专业人员和研究人员提供高质量的医学信息和研究分析。

## 功能特点

- **论文检索与分析**：搜索PubMed最新医学研究论文，并使用AI进行深度分析
- **医学问答**：基于最新医学研究回答专业医学问题
- **患者教育材料生成**：为患者创建易于理解的医学教育材料
- **向量数据库**：存储和检索相关医学论文，支持语义搜索
- **数据统计与可视化**：展示医学文献的统计信息和趋势

## 系统架构

```
📂 ai_med_assistant
│── 📂 src                  # 代码目录
│   │── pubmed_api.py       # 处理 PubMed 论文检索
│   │── gemini_ai.py        # 调用 Gemini API 解析论文
│   │── vector_db.py        # FAISS 向量数据库
│   │── app.py              # 主程序，运行 Streamlit
│── 📂 data                 # 存放抓取的论文数据
│── 📂 models               # 预训练的 NLP 模型
│── requirements.txt        # 依赖库
│── README.md               # 项目说明
```

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/medical-ai-assistant.git
cd medical-ai-assistant
```

2. 创建虚拟环境
```bash
python -m venv my_env
source my_env/bin/activate  # 在Windows上使用: my_env\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置API密钥
在生产环境中，建议使用环境变量存储API密钥，而不是硬编码在代码中。
```bash
export GEMINI_API_KEY="your_gemini_api_key"
```

## 使用方法

启动Streamlit应用：
```bash
cd src
streamlit run app.py
```

应用将在本地启动，通常在 http://localhost:8501 访问。

## 使用模式

### 1. 论文检索与分析
- 输入医学研究关键词搜索PubMed最新论文
- 选择单篇论文详细分析或多篇论文综合分析
- AI会提供结构化的论文分析，包括研究背景、方法、结论和临床意义等

### 2. 医学问答
- 直接向AI提问医学相关问题
- 可选择使用向量数据库中的相关论文作为回答依据
- 系统会提供基于证据的专业回答

### 3. 患者教育材料生成
- 输入医学主题，如"糖尿病自我管理"
- AI会生成结构化的患者教育材料
- 可下载生成的材料用于患者教育

### 4. 数据库统计
- 查看数据库中的论文统计信息
- 分析期刊分布和年份趋势
- 搜索数据库中的论文

## 技术栈

- **Google Gemini API**：提供AI大语言模型能力
- **PubMed API**：获取最新医学研究论文
- **FAISS**：高效向量相似度搜索
- **Sentence Transformers**：文本向量化
- **Streamlit**：构建交互式Web界面

## 注意事项

- 本助手提供的信息仅供参考，不应替代专业医疗建议
- API使用可能受到限制，请遵循相关服务提供商的使用政策
- 首次运行时，下载模型可能需要一些时间

## 未来计划

- 添加更多医学专业领域的知识
- 支持更多语言
- 集成更多医学数据库
- 增强论文分析能力

## 贡献指南

欢迎提交问题和拉取请求，共同改进这个项目。

## 许可证

[MIT License](LICENSE)
