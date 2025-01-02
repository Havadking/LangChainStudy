from langchain_openai import ChatOpenAI



llm = ChatOpenAI(
    temperature=0.1,
    openai_api_key="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",
    openai_api_base="https://openrouter.ai/api/v1",
    model="google/gemini-2.0-flash-exp:free"
)

print(llm.invoke("can you introduce yourself"))