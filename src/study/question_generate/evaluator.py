from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from src.model.DouBaoAILLM import DouBaoAILLM
from src.study.question_generate.book_question import Questions

# 这个用来对生成的问题进行评估以及纠错

llm = DouBaoAILLM()
parser = PydanticOutputParser(pydantic_object=Questions)
prompt = PromptTemplate(
    template="""
    你是一位资深的教育内容设计专家，结合中国考试中相关可d能的知识点，专注于为不同学习阶段设计高质量的选择题。请根据以下要求生成选择题：
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
        - options（选项）：该问题的选项，包括A、B、C、D是个选项，格式为：'A．选项的内容'
        - answer（答案）：该问题的正确答案
        - knowledge（知识点）：该问题属于那个知识点，包括：语言运用、修辞鉴赏、内容理解、主题思想、文化常识

    输出格式：{format_instructions}

    """,
    input_variables=["book", "carer", ],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser
