from langchain_core.output_parsers import StrOutputParser

from src.model.ZhipuAILLM import ZhipuAILLM
from langchain_core.prompts import ChatPromptTemplate
llm = ZhipuAILLM()
# output = llm.invoke("请你介绍一下你自己")
#
# print(output)

# 提示模板
# 这里我们要求模型对给定文本进行中文翻译
template = "你是一个翻译助手，可以帮助我将 {input_language} 翻译成 {output_language}."
human_template = "{text}"
# 构建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    ("human", human_template)
])
text = "我带着比身体重的行李，\
游入尼罗河底，\
经过几道闪电 看到一堆光圈，\
不确定是不是这里。\
"
# prompts = prompt.format_prompt(input_language="中文",
#                              output_language="英文",
#                              text=text)
# output = llm.invoke(prompts)
# print("output :", output)

# Output parser（输出解析器）
output_parser = StrOutputParser()
# parsed_output = output_parser.invoke(output)
# print("output_parser :", parsed_output)

chain = prompt | llm | output_parser
output = chain.invoke({"input_language": "中文", "output_language": "英文", "text": text})
print(output)


