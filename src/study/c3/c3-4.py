import os
from langchain_community.document_loaders import  PyMuPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.model.ZhipuAIEmbedding import ZhipuAIEmbeddings
from langchain_community.vectorstores import Chroma
from zhipuai import ZhipuAI

# 获取folder_path下所有文件路径，储存在file_paths里
file_paths = []
folder_path = '../../../data_base/knowledge_db'
for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        file_paths.append(file_path)
# print(file_paths[:3])

# 遍历文件路径并把实例化的loader存放在loaders里
loaders = []
for file_path in file_paths:

    file_type = file_path.split('.')[-1]
    if file_type == 'pdf':
        loaders.append(PyMuPDFLoader(file_path))
    elif file_type == 'md':
        loaders.append(UnstructuredMarkdownLoader(file_path))

# 下载文件并存储到texts
texts = []

for loader in loaders: texts.extend(loader.load())

text = texts[1]
# print(f"每一个元素的类型：{type(text)}.",
#     f"该文档的描述性数据：{text.metadata}",
#     f"查看该文档的内容:\n{text.page_content[0:]}",
#     sep="\n------\n")

# 切分文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50)

split_docs = text_splitter.split_documents(texts)

client = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")

# 定义embeddings
embeddings = ZhipuAIEmbeddings(client=client)

# 定义持久化路径
persist_directory = '../../../data_base/vector_db/chroma'

# 初始化向量数据库
vectordb = Chroma.from_documents(
    documents=split_docs[0:20], # 为了速度，只选择前 20 个切分的 doc 进行生成；使用千帆时因QPS限制，建议选择前 5 个doc
    embedding=embeddings,
    persist_directory=persist_directory
)

# 保存生成的向量数据库
# vectordb.persist()

print(f"向量库中存储的数量:{vectordb._collection.count()}")





