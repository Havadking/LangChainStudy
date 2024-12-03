from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_chroma import Chroma
from zhipuai import ZhipuAI

from src.model.ZhipuAIEmbedding import ZhipuAIEmbeddings
from src.model.ZhipuAILLM import ZhipuAILLM

client = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")
llm = ZhipuAILLM()
# 定义embeddings
embeddings = ZhipuAIEmbeddings(client=client)

persist_directory = "../../../data_base/vector_db/chroma"

vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# print(f"向量库中存储的数量：{vectordb._collection.count()}")
#
# question = "什么是南瓜书"
# docs = vectordb.similarity_search(question, k=3)
# print(f"检索到的内容数:{len(docs)}")
#
#
# for i, doc in enumerate(docs):
#     print(f"检索到的第{i}个内容: \n {doc.page_content}", end="\n-----------------------------------------------------\n")

# template = """
# 使用以下上下文来回答最后的问题。如果你不知道答案，就说你不知道，不要试图编造答
# 案。最多使用三句话。尽量使答案简明扼要。总是在回答的最后说“谢谢你的提问！”。
# {context}
# 问题: {question}
# """
#
# QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context","question"],
#                                  template=template)
# ## 创建一个基于模板的检索链
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     retriever=vectordb.as_retriever(),
#     return_source_documents=True,
#     chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
# )
#
# question_1 = "什么是南瓜书？"
# question_2 = "王阳明是谁？"
#
# # result = qa_chain({"query": question_1})
# # print("大模型+知识库后回答 question_1 的结果：")
# # print(result["result"])
#
# result = qa_chain({"query": question_2})
# print("大模型+知识库后回答 question_2 的结果：")
# print(result["result"])

memory = ConversationBufferMemory(
    memory_key="chat_history",  # 与 prompt 的输入变量保持一致
    return_messages=True  # 将以消息列表的形式返回聊天记录，而不是单个字符串
)

vectordb_retriever = vectordb.as_retriever()

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectordb_retriever,
    memory=memory
)

question = "我可以学习到关于提示工程的知识吗？"
result = qa({"question": question})
print(result['answer'])










