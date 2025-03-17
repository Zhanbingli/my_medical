import google.generativeai as genai
import json

# 配置Gemini API
# 注意：在生产环境中应该使用环境变量存储API密钥
genai.configure(api_key="AIzaSyB7P_GAybIqxXBtwFxrxQQCcCexipZdC-0")

class MedicalAssistant:
    """医学AI助手，基于Gemini API"""
    
    def __init__(self, model="gemini-pro"):
        self.model = model
        self.history = []
        self.system_prompt = """
        你是一位专业的医学AI助手，具有以下能力：
        1. 解析和总结最新医学研究论文
        2. 回答医学相关问题，包括诊断、治疗和预防等方面
        3. 提供基于证据的医学建议，并引用相关研究
        
        请注意：
        - 始终基于最新的医学研究提供信息
        - 明确指出医学共识与争议之处
        - 对于没有明确医学证据支持的内容，清楚说明这一点
        - 不要提供个人医疗建议，而是提供一般性的医学信息
        - 使用专业但易于理解的语言
        """
    
    def _call_gemini(self, prompt, temperature=0.2):
        """调用Gemini API"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # 添加历史对话
            for msg in self.history:
                messages.append(msg)
            
            # 添加当前问题
            messages.append({"role": "user", "content": prompt})
            
            response = genai.chat(model=self.model, messages=messages, temperature=temperature)
            
            # 保存对话历史
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": response.last})
            
            # 如果历史太长，删除最早的对话
            if len(self.history) > 10:
                self.history = self.history[-10:]
                
            return response.last
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    def parse_pubmed_article(self, article):
        """解析PubMed论文"""
        title = article.get('title', 'No title')
        abstract = article.get('abstract', 'No abstract')
        authors = article.get('authors', 'Unknown authors')
        journal = article.get('source', 'Unknown journal')
        pub_date = article.get('pub_date', 'Unknown date')
        
        prompt = f"""
        请对以下医学论文进行专业解析：
        
        标题: {title}
        作者: {authors}
        期刊: {journal}
        发表日期: {pub_date}
        摘要: {abstract}
        
        请提供以下分析：
        1. 研究背景与目的
        2. 研究方法与设计
        3. 主要研究发现
        4. 临床意义与应用
        5. 研究局限性
        6. 对医学实践的影响
        
        请以结构化的方式呈现，使用专业但易于理解的语言。
        """
        
        return self._call_gemini(prompt)
    
    def analyze_multiple_papers(self, articles):
        """分析多篇论文并综合结果"""
        if not articles:
            return "没有找到相关论文进行分析。"
        
        # 准备论文摘要
        papers_summary = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'No title')
            abstract = article.get('abstract', 'No abstract')
            authors = article.get('authors', 'Unknown authors')
            journal = article.get('source', 'Unknown journal')
            pub_date = article.get('pub_date', 'Unknown date')
            
            papers_summary += f"""
            论文 {i}：
            标题: {title}
            作者: {authors}
            期刊: {journal}
            发表日期: {pub_date}
            摘要: {abstract}
            
            """
        
        prompt = f"""
        请分析以下{len(articles)}篇最新医学研究论文，并提供综合性的分析报告：
        
        {papers_summary}
        
        请提供以下分析：
        1. 各研究的主要发现和共识点
        2. 研究之间的差异或矛盾之处
        3. 研究方法的优缺点比较
        4. 综合证据强度评估
        5. 对临床实践的建议
        6. 未来研究方向
        
        请以结构化的方式呈现，使用专业但易于理解的语言。
        """
        
        return self._call_gemini(prompt, temperature=0.3)
    
    def answer_medical_question(self, question, context_articles=None):
        """回答医学问题，可选择性地使用论文作为上下文"""
        
        context = ""
        if context_articles:
            context = "基于以下最新研究论文：\n\n"
            for i, article in enumerate(context_articles, 1):
                title = article.get('title', 'No title')
                abstract = article.get('abstract', 'No abstract')
                pub_date = article.get('pub_date', 'Unknown date')
                
                context += f"""
                论文 {i}：
                标题: {title}
                发表日期: {pub_date}
                摘要: {abstract}
                
                """
        
        prompt = f"""
        {context}
        
        请回答以下医学问题：
        {question}
        
        请提供：
        1. 直接回答问题
        2. 相关医学解释
        3. 如果有争议，说明不同观点
        4. 如果适用，提供预防或管理建议
        5. 引用支持你回答的研究证据
        
        请使用专业但易于理解的语言回答。
        """
        
        return self._call_gemini(prompt)
    
    def generate_patient_education(self, topic):
        """生成患者教育材料"""
        prompt = f"""
        请为患者创建一份关于"{topic}"的教育材料，内容应该：
        
        1. 使用简单易懂的语言解释医学概念
        2. 包含关键的健康信息和建议
        3. 解答患者常见问题
        4. 提供可靠的健康管理指导
        5. 说明何时应该寻求专业医疗帮助
        
        格式应该清晰、结构化，适合普通患者阅读理解。
        """
        
        return self._call_gemini(prompt)
    
    def clear_history(self):
        """清除对话历史"""
        self.history = []
        return "对话历史已清除。"

# 测试代码
if __name__ == "__main__":
    assistant = MedicalAssistant()
    example_text = "This study investigates the effects of..."
    print(assistant.parse_pubmed_article({
        'title': 'Effects of COVID-19 on respiratory system',
        'abstract': example_text,
        'authors': 'Smith J, Johnson A',
        'source': 'Journal of Medical Research',
        'pub_date': '2023-01-15'
    }))
