from typing import Annotated
import os

from langchain_community.tools import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from src.model.ZhipuAILLM import ZhipuAILLM

os.environ["TAVILY_API_KEY"] = "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"

# 增加一个搜索的工具
tool = TavilySearchResults(max_results=2)
tools = [tool]
# output = tool.invoke("what's a 'node' in LangGraph?")
# print(output)

# https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot

# 首先创建一个 StateGraph 。
# 一个 StateGraph 对象将我们聊天机器人的结构定义为“状态机”。
# 我们将添加 nodes 来表示llm以及聊天机器人可以调用的函数，
# 并添加 edges 来指定机器人应如何在这些函数之间进行转换。
class State(TypedDict):
    # Messages have the type "list".
    # The `add_messages` function in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


"""
在定义图时，第一步是定义其 State 。 
State 包括图的架构和处理状态更新的 reducer 函数。
在我们的示例中， State 是一个具有一个键的 TypedDict ： messages 。 
add_messages reducer 函数用于将新消息追加到列表中，而不是覆盖它。
没有 reducer 注解的键将覆盖之前的值。
"""


graph_builder = StateGraph(State)

# 我们的图表现在可以处理两个关键任务：
# 1. 每个 node 可以接收当前的 State 作为输入，并输出对状态的更新。
# 2. 对 messages 的更新将追加到现有列表中，而不是覆盖它，这得益于与 Annotated 语法一起使用的预构建 add_messages 函数。

# 接下来，添加一个“ chatbot ”节点。
# 节点代表工作单元。它们通常是常规的 Python 函数。

llm = ZhipuAILLM()
# 在llm处添加搜索工具
# Modification: tell the LLM which tools it can call
llm_with_tools = llm.bind_tools(tools=tools)


# 创建一个检查点(这里为了学习使用内存的存储，用于生产的时候可以sqlite存储)
memory = MemorySaver()


# def route_tools(state: State):
#     """
#     Use in the conditional_edge to route to the ToolNode if the last message
#     has tool calls. Otherwise, route to the end.
#     """
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif messages := state.get("messages", []):
#         ai_message = messages[-1]
#     else:
#         raise ValueError(f"No messages found in input state to tool_edge: {state}")
#
#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return "tools"
#
#     return END


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
## 创建并添加tool_node
# tool_node = BasicToolNode(tools=tools)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
# graph_builder.add_conditional_edges(
#     "chatbot",
#     route_tools,
#     # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
#     # It defaults to the identity function, but if you
#     # want to use a node named something else apart from "tools",
#     # You can update the value of the dictionary to something else
#     # e.g., "tools": "my_tools"
# {"tools": "tools", END: END},
# )
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
# graph_builder.add_edge("chatbot", END)

# 1.编译的时候添加记忆
# 2.编译的时候添加 human-in-the-loop
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["tools"]
)

# 首先，选择一个线程作为本次对话的键
config = {"configurable": {"thread_id": "1"}}
user_input = "I'm learning LangGraph. Could you do some research on it for me?"

# user_input = "Hi there! My name is Will."
# The config is the **second positional argument** to stream() or invoke()!

events = graph.stream({"messages": [("user", user_input)]}, config=config, stream_mode="values")

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
    # print(event)

# 在这里，当要调用tools的时候，暂停了
snapshot = graph.get_state(config)
print(snapshot.next)

# 查看一下当前要进行的状态的内容
existing_message = snapshot.values["messages"][-1]
print(existing_message.tool_calls)

# 然后继续手动执行
events = graph.stream(None, config=config, stream_mode="values")

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()




#
# user_input = "Remember my name?"
#
# # The config is the **second positional argument** to stream() or invoke()!
# events = graph.stream(
#     {"messages": [("user", user_input)]}, config, stream_mode="values"
# )
# for event in events:
#     event["messages"][-1].pretty_print()

# 打印看看我们构建的图
# png = graph.get_graph().draw_mermaid()
# print(png)


def stream_graph_updates(user_input: str):
    for event in graph.stream(
            input={"messages": [("user", user_input)]},
            config=config,
    ):
        # print(event)
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)



# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#
#         stream_graph_updates(user_input)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break














