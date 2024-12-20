import logging

import bs4
from langchain.retrievers import MultiQueryRetriever
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from zhipuai import ZhipuAI

from src.model.ZhipuAIEmbedding import ZhipuAIEmbeddings
from src.model.ZhipuAILLM import ZhipuAILLM

# https://python.langchain.com/docs/how_to/MultiQueryRetriever/


logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only = bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    )
)

data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

splits = text_splitter.split_documents(data)

# 创建需要的模型
llm = ZhipuAILLM()
client = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")
# 创建需要的向量
embeddings = ZhipuAIEmbeddings(client=client)

vectordb = Chroma.from_documents(documents=splits, embedding=embeddings)


question = "What are the approaches to Task Decomposition?"

retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectordb.as_retriever(),
    llm=llm
)

unique_docs = retriever_from_llm.invoke(question)
print(len(unique_docs))
print(unique_docs)




















