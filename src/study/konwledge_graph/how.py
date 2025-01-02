import os

from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

from src.model.DeepSeekAILLM import DeepSeekAILLM
from src.model.DouBaoAILLM import DouBaoAILLM

# 1. 从文本中提取结构化信息：该模型用于从文本中提取结构化图信息。
# 2. 存储到图数据库：将提取的结构化图信息存储到图数据库中，支持下游的 RAG 应用

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "fractal-clone-alice-bonanza-adios-4522"

graph = Neo4jGraph(refresh_schema=False)
# 通过利用LLM来解析和分类实体及其关系，将文本文档转换为结构化图文档
llm = DeepSeekAILLM()
llm_transformer_props = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Country", "Organization"],
    allowed_relationships=["NATIONALITY", "LOCATED_IN", "WORKED_AT", "SPOUSE"],
    node_properties=["born_year"],
)

text = """
    Marie Curie, born in 1867, was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.
    She was the first woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the only person to win a Nobel Prize in two scientific fields.
    Her husband, Pierre Curie, was a co-winner of her first Nobel Prize, making them the first-ever married couple to win the Nobel Prize and launching the Curie family legacy of five Nobel Prizes.
    She was, in 1906, the first woman to become a professor at the University of Paris.
    """

documents = [Document(page_content=text)]
graph_documents_props = llm_transformer_props.convert_to_graph_documents(documents)

print(f"Nodes:{graph_documents_props[0].nodes}")
print(f"Relationships:{graph_documents_props[0].relationships}")

graph.add_graph_documents(graph_documents_props)
