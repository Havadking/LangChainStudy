from typing import Any

from langchain_openai import ChatOpenAI
from src.constants import DeepSeekConstants


class DeepSeekAILLM(ChatOpenAI):
    """
    DeepSeekAILLM: A class for interacting with the DeepSeek API.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(temperature=DeepSeekConstants.TEMPERATURE,
                         model=DeepSeekConstants.MODEL,
                         openai_api_key=DeepSeekConstants.OPENAI_API_KEY,
                         openai_api_base=DeepSeekConstants.OPENAI_API_BASE, **kwargs)
