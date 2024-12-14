from typing import Optional, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import tool_example_to_messages
from pydantic import BaseModel, Field
from src.model.ZhipuAILLM import ZhipuAILLM



# 教程地址：https://python.langchain.com/docs/tutorials/extraction/


# 首先描述需要提取那些信息
# 定义架构时有两个最佳实践：
# 记录属性和模式本身：此信息发送至LLM，用于提高信息提取的质量。`"""Information about a person."""`
# 不要强迫LLM编造信息！上面我们使用了 Optional 来允许LLM在不知道答案时输出 None 。

class Person(BaseModel):
    """Information about a person."""
    # ^ Doc-string for the entity Person.
    # This doc-string is sent to the LLM as the description of the schema Person,
    # and it can help to improve extraction results.

    # Note that:
    # 1. Each field is an `optional` -- this allows the model to decline to extract it!
    # 2. Each field has a `description` -- this description is used by the LLM.
    # Having a good description can help improve extraction results.

    name: Optional[str] = Field(default=None, description="The name of the person")
    hair_color: Optional[str] = Field(
        default=None, description="The color of the person's hair if known"
    )
    height_in_meters: Optional[str] = Field(
        default=None, description="Height measured in meters"
    )

class Data(BaseModel):
    """Extracted data about people."""

    # Creates a model so that we can extract multiple entities.
    people: List[Person]

# Define a custom prompt to provide instructions and any additional context.
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

llm = ZhipuAILLM()
structured_llm = llm.with_structured_output(schema=Data)

# text = "My name is Jeff, my hair is black and i am 6 feet tall. Anna has the same color hair as me."
# prompt = prompt_template.invoke({"text": text})
# output = structured_llm.invoke(prompt)
#
# print(output.dict())


# LangChain 包含一个实用函数 tool_example_to_messages，可以为大多数模型提供商生成有效的序列。
# 它通过仅需要相应工具调用的 Pydantic 表示，简化了结构化少量示例的生成

examples = [
    (
        "The ocean is vast and blue. It's more than 20,000 feet deep.",
        Data(people=[]),
    ),
    (
        "Fiona traveled far from France to Spain.",
        Data(people=[Person(name="Fiona", height_in_meters=None, hair_color=None)]),
    ),
]
messages = []

for txt, tool_call in examples:
    messages.extend(tool_example_to_messages(txt, [tool_call]))

for message in messages:
    message.pretty_print()

# 不提供示例的情况(提供示例的情况下)
message_no_extraction = {
    "role": "user",
    "content": "The solar system is large, but earth has only 1 moon.",
}
output = structured_llm.invoke(messages + [message_no_extraction])
print(output)
