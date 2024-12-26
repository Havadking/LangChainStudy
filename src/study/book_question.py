import json
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.model.ZhipuAILLM import ZhipuAILLM


# 定义输出的格式
class Question(BaseModel):
    """Information about a person."""
    question: str = Field(description="问题")
    options: List[str] = Field(description="该问题的四个选项")
    answer: str = Field(description="问题的答案", examples=["A", "B", "C", "D"])
class Questions(BaseModel):
    """A collection of some questions"""
    questions: List[Question] = Field(description="问题的集合")
# 定义输出解释器
parser = PydanticOutputParser(pydantic_object=Questions)
# 定义提示词和所需参数
prompt = PromptTemplate(
    template="""
    你是一位资深的教育内容设计专家，专注于为不同学习阶段设计高质量的选择题。请根据以下要求生成选择题：
    根据书名 {book} 的内容，设计与书本相关的选择题。
    选择题需要覆盖整本书的主要内容，包括但不限于故事情节、主题思想、人物特征、重要场景和核心概念，尽量减少出现猜人物的问题。
    按照严格的 JSON 格式生成{num}道选择题，每题包含4个选项，其中只有1个正确答案，其他3个为具有一定迷惑性的错误答案。
    选项设置需符合 {carer} 学生的理解能力（小学、初中、高中），并确保问题和答案语言表达清晰、简洁。
    保持题目的趣味性和互动性，避免过于晦涩难懂。
    
    每个问题必须包括：
        - question（问题）：问题的描述
        - options（选项）：该问题的选项，包括A、B、C、D是个选项
        - answer（答案）：该问题的正确答案
    
    示例输入：
    
        书名：哈利·波特与魔法石
        适用阶段：初中
        
    示例输出：

        问题：哈利第一次收到录取通知书时，它是通过什么方式送达的？
        A. 猫头鹰邮递 
        B. 魔法传送门
        C. 学校特使送来
        D. 普通邮件
        正确答案：A

        问题：海格从古灵阁取出的包裹中装了什么？
        A. 一颗宝石
        B. 魔法石
        C. 魔杖
        D. 隐形斗篷
        正确答案：B

        ……

    输出格式：{format_instructions}

    注意事项：

    题目内容需完全基于书籍内容。
    适用阶段的知识范围和语言风格需要严格符合指定阶段。
    执行格式： 将生成的选择题以清单形式输出，每题包括问题、选项（A/B/C/D）和正确答案。
    """,
    input_variables=["book", "num", "carer"],
    partial_variables= {"format_instructions": parser.get_format_instructions()}
)
# 定义大模型
llm = ZhipuAILLM()
# 组装成链
chain  = prompt | llm | parser

def generateQuestions(book:str, num:int, carer: str):
    print(f"开始生成《{book}》相关的题目")
    output = chain.invoke(
        {
            "book": book,
            "num": num,
            "carer": carer
        }
    )
    output_dict = output.dict()

    # print(output_dict)

    # 保存为 JSON 文件
    with open(book +".json", "w", encoding="utf-8") as json_file:
        json.dump(output_dict, json_file, ensure_ascii=False, indent=4)

    print(f"成功生成{num}个《{book}》相关的题目")



if __name__ == '__main__':
    books = ["三国演义", "钢铁是怎样炼成的", "麦田里的守望者", "瓦尔登湖"]
    num_of_question = 5
    for_who = "高中"

    for book in books:
        generateQuestions(book, num_of_question, for_who)

    generateQuestions(book, num_of_question, for_who)


