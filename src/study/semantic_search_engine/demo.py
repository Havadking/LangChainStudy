from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from zhipuai import ZhipuAI

from src.model.ZhipuAIEmbedding import ZhipuAIEmbeddings

# 教程：https://python.langchain.com/docs/tutorials/retrievers/


# 1. 加载文件
file_path = "../../../resource/nke-10k-2023.pdf"
loader = PyMuPDFLoader(file_path)

docs = loader.load()

print(len(docs))

# 2.拆分
# 将文档分割成每块 1000 个字符，块与块之间有 200 个字符的重叠。
# 这种重叠有助于减少将一个语句与其相关的重要上下文分离的可能性。

# 使用 RecursiveCharacterTextSplitter，它将递归地使用常见的分隔符（如换行符）来分割文档，
# 直到每个块达到适当的大小。这是推荐用于通用文本使用场景的文本分割器。

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)

all_splits = text_splitter.split_documents(docs)

print(len(all_splits))

# 3.向量
# 向量搜索是一种常见的存储和搜索非结构化数据（如非结构化文本）的方法。
# 其思想是存储与文本相关联的数值向量。
# 给定一个查询，我们可以将其嵌入为相同维度的向量，并使用向量相似性度量（如余弦相似性）来识别相关文本。

# 向量存储
# LangChain VectorStore 对象包含将文本和 Document 对象添加到存储库中的方法，并使用各种相似性度量来查询它们。
# 它们通常使用嵌入模型初始化，这些模型决定了文本数据如何转换为数值向量。
client = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")
embeddings = ZhipuAIEmbeddings(client=client)
vector_store = InMemoryVectorStore(embeddings)

# 实例化我们的向量存储后，我们现在可以索引文档。
ids = vector_store.add_documents(documents=all_splits)

# print(ids)

# 嵌入通常将文本表示为“密集”向量，使得语义相似的文本在几何上接近。
# 这使我们只需输入一个问题就能检索到相关信息，而无需了解文档中使用的任何特定关键词

# results = vector_store.similarity_search("How many distribution centers does Nike have in the US?")
#
# print(results[0])

# VectorStores 实现了一个 as_retriever 方法，该方法将生成一个检索器，具体来说是 VectorStoreRetriever。
# 这些检索器包括特定的 search_type 和 search_kwargs 属性，用于识别要调用底层向量存储的哪些方法，

retriever = vector_store.as_retriever()

batch = retriever.batch(["How many distribution centers does Nike have in the US?", "When was Nike incorporated?", ])

print(batch)










