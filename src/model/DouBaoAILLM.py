from typing import Any

from langchain_openai import ChatOpenAI
from src.constants import DouBaoConstants


class DouBaoAILLM(ChatOpenAI):
    """
    DouBaoAILLM: A class for interacting with the ZhipuAI API.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(temperature=DouBaoConstants.TEMPERATURE,
                         model=DouBaoConstants.MODEL,
                         openai_api_key=DouBaoConstants.OPENAI_API_KEY,
                         openai_api_base=DouBaoConstants.OPENAI_API_BASE, **kwargs)
