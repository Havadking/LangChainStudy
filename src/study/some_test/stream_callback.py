from langchain_core.callbacks import StreamingStdOutCallbackHandler

from src.model.ZhipuAILLM import ZhipuAILLM

llm = ZhipuAILLM(
    streaming=True
)

# 调用流式生成
generator = llm.stream("请告诉我一个笑话")

# 收集所有生成的内容
result = ""
for chunk in generator:
    if chunk is None:
        break  # 流式结束
    result += chunk.content  # 拼接生成的内容

print("完整输出:", result)
