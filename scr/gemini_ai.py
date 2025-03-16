import google.generativeai as genai

genai.configure(api_key="AIzaSyB7P_GAybIqxXBtwFxrxQQCcCexipZdC-0")

def parse_pubmed_article(article_text):
    """用 Gemini AI 解析论文内容"""
    prompt = f"""
    请对以下医学论文进行结构化解析：
    1. 研究背景
    2. 研究方法
    3. 研究结论
    4. 主要数据
    5. 临床意义
    6. 研究局限性

    论文内容：
    {article_text}
    """
    response = genai.chat(model="gemini-pro", messages=[{"role": "user", "content": prompt}])
    return response.last

if __name__ == "__main__":
    example_text = "This study investigates the effects of..."
    print(parse_pubmed_article(example_text))
