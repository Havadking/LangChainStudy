from zhipuai import ZhipuAI

client = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")
response = client.embeddings.create(
    model="embedding-3", #填写需要调用的模型编码
     input=[
        "美食非常美味，服务员也很友好。",
        "这部电影既刺激又令人兴奋。",
        "阅读书籍是扩展知识的好方法。"
    ],
)
print(response)