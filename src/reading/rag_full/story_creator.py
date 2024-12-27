from langchain_core.prompts import ChatPromptTemplate

from src.xxt_ai_chat.xxt_common.llm.zhipu_llm import ZhipuAILLM
from src.reading.rag_full.rag_langchain import FaissSearch, tokenize_chinese

template = """
检索结果:
第1个段落:
{doc}
检索语句: 你的名字是启迪绘，擅长把科学事实编成有趣易懂的故事，以激发儿童对相关领域的好奇心，同时这个故事应当作为成为亲子共读的桥梁，助力孩子们在轻松愉快的氛围中学习成长。
你需要根据我的问题和你所知道的知识为我创作符合以上要求的故事。
我的问题是：
{query}
请根据以上检索结果回答检索语句的问题
"""
input_text = "什么是天文学"
search_engine = FaissSearch(path='./faiss_index_llama_full_ernie', top_k=5, threshold=10)
llm = ZhipuAILLM()

class StoryCreator:
    def __init__(self):
        pass


def ragAndStory(text):
    # 1. 执行检索
    docs = search_engine.search(text)
    if len(docs) > 0:
        # 取出检索到的相关性最高的文档
        doc = docs[0]['content']
    else:
        # 如果没有检索到相关文档，则将doc置为空字符串
        doc = ""
    # 2. 构建prompt
    prompt = ChatPromptTemplate.from_template(template)
    # 3. 执行问答
    chain = prompt | llm
    messages = chain.invoke({"query": input_text, "doc": doc})
    # print(messages)
    # print(messages.content)
    # print()
    print("生成故事消耗的token为:" + str(messages.response_metadata['token_usage']['total_tokens']))
    return messages.content




