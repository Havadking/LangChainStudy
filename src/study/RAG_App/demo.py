import os
from typing import  List, Annotated, Literal

import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
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

# print(all_splits[0].metadata)

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
将下面的内容从英文翻译为中文。
{context}
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



graph_builder = StateGraph(MessagesState)


# 转换为一个工具
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to the query."""
    retrieved_docs = vector_store.similarity_search(query=query, k=2)
    serialized = "\n\n".join(
        f"Source:{doc.metadata}\n" f"Content:{doc.page_content}"
         for doc in retrieved_docs
    )
    return serialized, retrieved_docs


# @tool(response_format="content")
# def translate(query: str):
#     """Translate English content into Chinese."""
#     messages = translate_prompt.invoke(
#         {
#             "context": query
#         }
#     )
#     response = llm.invoke(messages)
#     return response.content


def translate(state: MessagesState):
    messages = translate_prompt.invoke(
        {
            "context": state["messages"][-1].content
        }
    )
    response = llm.invoke(messages)
    return {"messages": response}


# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_response(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Step 2: Execute the retrieval
tools = ToolNode([retrieve])

# Step 3: Generate a response using the retrieved content
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(
        doc.content for doc in tool_messages
    )
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}


# Create Agent
memory = MemorySaver()
agent_executor = create_react_agent(llm, [retrieve], checkpointer=memory)

# mermaid = agent_executor.get_graph().draw_mermaid()
# print(mermaid)

config = {"configurable": {"thread_id": "def234"}}

# 关键区别在于，这里工具调用会循环回到最初的LLM调用，
# 而不是以一个最终生成步骤结束运行。
# 模型可以利用检索到的上下文来回答问题，
# 或者生成另一个工具调用以获取更多信息。
input_message = (
    "What is the standard method for Task Decomposition?\n\n"
    "Once you get the answer, look up common extensions of that method."
)

for event in agent_executor.stream(
    {"messages": [{"role": "user", "content": input_message}]},
    stream_mode="values",
    config=config,
):
    event["messages"][-1].pretty_print()





# graph_builder.add_node(query_or_response)
# graph_builder.add_node(tools)
# graph_builder.add_node(generate)
# graph_builder.add_node(translate)
#
# graph_builder.set_entry_point("query_or_response")
# graph_builder.add_conditional_edges(
#     "query_or_response",
#     tools_condition,
#     {END: END, "tools": "tools"}
# )
# graph_builder.add_edge("tools", "generate")
# graph_builder.add_edge("generate", END)
# graph_builder.add_edge("generate", "translate")
# graph_builder.add_edge("translate", END)
#
# # Add Memory
# memory = MemorySaver()
# graph = graph_builder.compile(checkpointer=memory)
#
# # Specify an ID for the thread
# config = {"configurable": {"thread_id": "abc123"}}
#
#
# input_message = "What is Task Decomposition?"
# input_message2 = "Can you look up some common ways of doing it?"
# # input_message = "What's 329993 divided by 13662?"
#
# for step in graph.stream(
#     {"messages": [{"role": "user", "content": input_message}]},
#     stream_mode="values",
#     config=config
# ):
#     step["messages"][-1].pretty_print()
#
# for step in graph.stream(
#     {"messages": [{"role": "user", "content": input_message2}]},
#     stream_mode="values",
#     config=config
# ):
#     step["messages"][-1].pretty_print()
#


# # 定义执行步骤的方法
#
# def analyze_query(state: State):
#     print("状态执行到analyze_query咯")
#     structured_llm = llm.with_structured_output(schema=Search)
#     query = structured_llm.invoke(input=state["question"])
#     return {"query": query}
#
#
# def retrieve(state: State):
#     print("状态执行到retrieve咯")
#     query = state["query"]
#     retrieved_docs = vector_store.similarity_search(
#         query["query"],
#         filter=lambda doc: doc.metadata.get("section") == query["section"]
#     )
#     return {"context": retrieved_docs}
#
# # def translate(state: State):
# #     print("状态执行到translate咯")
# #     messages = translate_prompt.invoke(
# #         {
# #             "context": state["answer"]
# #         }
# #     )
# #     response = llm.invoke(messages)
# #     return {"answer": response.content}
#
# def generate(state: State):
#     print("状态执行到generate咯")
#     docs_content = "\n\n".join(doc.page_content for doc in state["context"])
#     messages = prompt.invoke(
#         {
#             "question": state["question"],
#             "context": docs_content
#         }
#     )
#     response = llm.invoke(messages)
#     return {"answer": response.content}
#
#
# # 构建graph
# graph_builder = StateGraph(State)
# graph_builder.add_node("retrieve", retrieve)
# graph_builder.add_node("generate", generate)
# graph_builder.add_node("translate", translate)
# graph_builder.add_node("analyze_query", analyze_query)
# # graph_builder.add_sequence([retrieve, generate])
# graph_builder.add_edge(START, "analyze_query")
# # graph_builder.add_edge(START, "retrieve")
# graph_builder.add_edge("analyze_query", "retrieve")
# graph_builder.add_edge("retrieve", "generate")
# graph_builder.add_edge("generate", "translate")
# graph_builder.add_edge("translate", END)
# graph = graph_builder.compile()
#
# # print(graph.get_graph().draw_mermaid())
# # print(graph.get_graph().draw_ascii())
#
# # for step in graph.stream(
# #     {"question": "What does the end of the post say about Task Decomposition?"},
# #     stream_mode="updates",
# # ):
# #     print(f"{step}\n\n----------------\n")
# response = graph.invoke({"question": "What does the end of the post say about Task Decomposition?"})
#
# print(response["answer"])























