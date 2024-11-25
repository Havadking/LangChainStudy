from typing import Any

import streamlit as st
from langchain_openai import ChatOpenAI


class ZhipuAILLM(ChatOpenAI):
    """
    ZhipuAILLM: A class for interacting with the ZhipuAI API.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(temperature=0.1,
                         model="glm-4-plus",
                         openai_api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY",
                         openai_api_base="https://open.bigmodel.cn/api/paas/v4/", **kwargs)


def generate_response(input_text):
    llm = ZhipuAILLM()
    # st.info(llm(input_text).content)
    return llm.invoke(input_text).content

def main():
    st.title('🦜🔗 动手学大模型应用开发')

    # 用于跟踪对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    messages = st.container(height=300)

    if prompt := st.chat_input("Say something"):
        # 将用户输入添加到对话历史中
        st.session_state.messages.append(
            {
                "role": "user",
                "text": prompt
            }
        )
        # 调用respond函数生成回答
        answer = generate_response(prompt)

        # 检查回答是否为 None
        if answer is not None:
            # 将LLM的回答添加到对话历史中
            st.session_state.messages.append(
                {"role": "assistant",
                 "text": answer
                 }
            )
        # 显示整个对话历史
        for message in st.session_state.messages:
            if message["role"] == "user":
                messages.chat_message("user").write(message["text"])
            elif message["role"] == "assistant":
                messages.chat_message("assistant").write(message["text"])


if __name__ == '__main__':
    main()