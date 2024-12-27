import random
import concurrent.futures

from langchain_core.prompts import ChatPromptTemplate

from src.xxt_ai_chat.xxt_common.llm.zhipu_llm import ZhipuAILLM
from src.reading.rag_full.resources_creator import generate_voice, generate_image, save_script, save_story, \
    generate_video
from src.reading.rag_full.script_creator import ScriptCreator
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
search_engine = FaissSearch(path='./faiss_index_llama_full_ernie', top_k=5, threshold=10)
llm = ZhipuAILLM()
script_creator = ScriptCreator()


def rag_and_story(text):
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
    print("开始生成故事")
    messages = chain.invoke({"query": text, "doc": doc})
    # print(messages)
    # print(messages.content)
    # print()
    print("生成故事消耗的token为:" + str(messages.response_metadata['token_usage']['total_tokens']))
    return messages.content


def process_story(story, uid, index):
    dialog = story['background']
    background = story['background']
    generate_image(background, uid, index + 1)

    # 拼接完整对话和背景音
    for line in story["dialog"]:
        dialog += line
    dialog += story['narration']

    # 生成音频并保存
    generate_voice(dialog, uid, index + 1)


if __name__ == '__main__':
    uid = random.randint(10000, 99999)
    # 1.通过问题进行rag检索然后生成故事
    question = "天上有多少个星座？"
    story = rag_and_story(question)
    print("生成的故事内容为:\n" + story)
    save_story(story, uid)

    # 2.根据生成的故事，生成对应的剧本
    script = script_creator.create_script(story)
    print("生成的剧本为:\n")
    print(script)

    # 3.根据生成的剧本，生成对应的音频和图片
    script_dict = script.dict()  # 将返回格式（自定义格式）转换为字典并进行操作
    save_script(script_dict, uid)
    # 改用多线程
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_story, story, uid, index)
            for index, story in enumerate(script_dict["stories"])
        ]

    # 4.根据生成的图片和音频合成视频
    generate_video(uid)
