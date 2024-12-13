from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.model.ZhipuAILLM import ZhipuAILLM
# 教程地址：https://python.langchain.com/docs/tutorials/classification/

# 对一段文本进行标注
# 具体来说，我们可以定义：
#
# 每个属性的可能值
# 描述以确保模型理解该属性
# 返回所需属性

tagging_prompt = ChatPromptTemplate.from_template(
    """
    Extract the desired information from the following passage.
    Only extract the properties mentioned in the 'Classification' function.
    Passage:
    {input}
    """
)

class Classification(BaseModel):
    sentiment: str = Field(description="The sentiment of the text", examples=["happy", "neutral", "sad"])
    aggressiveness: int = Field(description="How aggressive the text is on a scale from 1 to 10", examples=[1, 2, 3, 4, 5])
    language: str = Field(description="The language the text is written in", examples=["spanish", "english", "Chinese", "german", "italian"])

llm = ZhipuAILLM().with_structured_output(
    Classification
)

input = "我真的不知道该怎么说你好了，连怎么简单的事情都做不好"

prompt = tagging_prompt.invoke({"input": input})
response = llm.invoke(prompt)
print(response.dict())
















