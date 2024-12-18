import os
from typing import  List, Annotated, Literal

import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from zhipuai import ZhipuAI

from src.model.ZhipuAIEmbedding import ZhipuAIEmbeddings
from src.model.ZhipuAILLM import ZhipuAILLM

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"LangSmith-start"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"

# 创建需要的模型
llm = ZhipuAILLM()
client = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")
# 创建需要的向量
embeddings = ZhipuAIEmbeddings(client=client)
vector_store = InMemoryVectorStore(embedding=embeddings)

# load and chunk contents of the blog
# 加载博客的内容
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only = bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    )
)

docs = loader.load()
# 切分
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
all_splits = text_splitter.split_documents(documents=docs)

# 添加一些假数据,假设其有一定的期限
total_documents = len(all_splits)
third = total_documents // 3
for i, document in enumerate(all_splits):
    if i < third:
        document.metadata["section"] = "beginning"
    elif i < 2 * third:
        document.metadata["section"] = "middle"
    else:
        document.metadata["section"] = "end"

print(all_splits[0].metadata)

_ = vector_store.add_documents(documents=all_splits)


class Search(TypedDict):
    """Search query."""
    query: Annotated[str, ..., "Search query to run"]
    section: Annotated[
        Literal["beginning", "middle", "end"],
        ...,
        "Section to query."
    ]

# 提示词
# prompt = hub.pull("rlm/rag-prompt")
template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question}
Context: {context}
Answer:
"""

translate_template = """
你是一个翻译大师，请将下面的内容翻译为中文。
Context: {context}
Answer:
"""

translate_prompt = PromptTemplate(
    template=translate_template,
    input_variables=["context"],
)
prompt = PromptTemplate(
    template=template,
    input_variables=["question", "context"],
)
# prompt.pretty_print()

# 定义State
class State(TypedDict):
    question: str
    query: Search
    context: List[Document]
    answer: str

# 定义执行步骤的方法

def analyze_query(state: State):
    print("状态执行到analyze_query咯")
    structured_llm = llm.with_structured_output(schema=Search)
    query = structured_llm.invoke(input=state["question"])
    return {"query": query}


def retrieve(state: State):
    print("状态执行到retrieve咯")
    query = state["query"]
    retrieved_docs = vector_store.similarity_search(
        query["query"],
        filter=lambda doc: doc.metadata.get("section") == query["section"]
    )
    return {"context": retrieved_docs}

def translate(state: State):
    print("状态执行到translate咯")
    messages = translate_prompt.invoke(
        {
            "context": state["answer"]
        }
    )
    response = llm.invoke(messages)
    return {"answer": response.content}

def generate(state: State):
    print("状态执行到generate咯")
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke(
        {
            "question": state["question"],
            "context": docs_content
        }
    )
    response = llm.invoke(messages)
    return {"answer": response.content}


# 构建graph
graph_builder = StateGraph(State)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)
graph_builder.add_node("translate", translate)
graph_builder.add_node("analyze_query", analyze_query)
# graph_builder.add_sequence([retrieve, generate])
graph_builder.add_edge(START, "analyze_query")
# graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("analyze_query", "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", "translate")
graph_builder.add_edge("translate", END)
graph = graph_builder.compile()

print(graph.get_graph().draw_mermaid())
# print(graph.get_graph().draw_ascii())

for step in graph.stream(
    {"question": "What does the end of the post say about Task Decomposition?"},
    stream_mode="updates",
):
    print(f"{step}\n\n----------------\n")























