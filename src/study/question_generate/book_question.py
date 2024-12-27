import json
from typing import List

from langchain_community.callbacks import OpenAICallbackHandler, get_openai_callback
from langchain_core.callbacks import CallbackManager
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.model.DouBaoAILLM import DouBaoAILLM
from src.model.ZhipuAILLM import ZhipuAILLM

callback_manager = CallbackManager([OpenAICallbackHandler()])




# 定义输出的格式
class Question(BaseModel):
    """question of the book."""
    question: str = Field(description="问题")
    options: List[str] = Field(description="该问题的四个选项")
    answer: str = Field(description="问题的答案", examples=["A", "B", "C", "D"])

class Knowledge(BaseModel):
    """classify question by knowledge"""
    knowledge: str = Field(description="问题的分类", examples=["语言运用","修辞鉴赏","内容理解","主题思想","文化常识"])
    questions: List[Question] = Field(description="问题的集合")

class Questions(BaseModel):
    """A collection of some questions"""
    questions: List[Knowledge] = Field(description="根据知识点分类的问题的集合")
# 定义输出解释器
parser = PydanticOutputParser(pydantic_object=Questions)
# 定义提示词和所需参数
prompt = PromptTemplate(
    template="""
    你是一位资深的教育内容设计专家，专注于为不同学习阶段设计高质量的选择题。请根据以下要求生成选择题：
    根据书名 {book} 的内容，设计与书本相关的选择题。
    选择题需要覆盖整本书的主要内容，包括但不限于故事情节、主题思想、人物特征、重要场景和核心概念，尽量减少出现猜人物的问题。
    按照严格的 JSON 格式生成10道选择题，每题包含4个选项，其中只有1个正确答案，其他3个为具有一定迷惑性的错误答案。
    题目分为5个知识点（语言运用、修辞鉴赏、内容理解、主题思想、文化常识），每个知识点生成2道题目。
    选项设置需符合 {carer} 学生的理解能力（小学、初中、高中），并确保问题和答案语言表达清晰、简洁。
    保持题目的趣味性和互动性，避免过于晦涩难懂。
    题目内容需完全基于书籍内容。
    适用阶段的知识范围和语言风格需要严格符合指定阶段。
    
    生成的每个选择题必须严格的包括一下的字段：
        - question（问题）：问题的描述
        - options（选项）：该问题的选项，包括A、B、C、D是个选项
        - answer（答案）：该问题的正确答案
        - knowledge（知识点）：该问题属于那个知识点，包括：语言运用、修辞鉴赏、内容理解、主题思想、文化常识

    输出格式：{format_instructions}

    """,
    input_variables=["book", "carer",],
    partial_variables= {"format_instructions": parser.get_format_instructions()}
)
# 定义大模型
# llm = ZhipuAILLM()
llm = DouBaoAILLM()
# 组装成链
chain  = prompt | llm | parser
# chain = chain.bind(callback_manager=callback_manager, verbose=True)

def generateQuestions(book:str, num:int, carer: str):
    print(f"开始生成《{book}》相关的题目")
    with get_openai_callback() as cb:
        output = chain.invoke(
            {
                "book": book,
                "carer": carer,
            }
        )
        print(cb)

    # print(output.usage_metadata)

    output_dict = output.dict()
    # handler = callback_manager.handlers[0]
    # print(f"Prompt Tokens: {handler.prompt_tokens}")
    # print(f"Completion Tokens: {handler.completion_tokens}")
    # print(f"Total Tokens: {handler.total_tokens}")
    # print(f"Execution Time (s): {handler.execution_time}")

    # print(output_dict)

    # 保存为 JSON 文件
    with open(book +".json", "w", encoding="utf-8") as json_file:
        json.dump(output_dict, json_file, ensure_ascii=False, indent=4)

    print(f"成功生成{num}个《{book}》相关的题目")



if __name__ == '__main__':
    # books = ["三国演义", "钢铁是怎样炼成的", "麦田里的守望者", "瓦尔登湖", "活着"]
    # num_of_question = 3
    # for_who = "高中"
    #
    # for book in books:
    #     generateQuestions(book, num_of_question, for_who)

    generateQuestions("活着", 10, "高中")


