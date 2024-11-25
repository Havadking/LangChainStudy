from typing import Any

from langchain_openai import ChatOpenAI
from src.constants import ZhiPuConstants


class ZhipuAILLM(ChatOpenAI):
    """
    ZhipuAILLM: A class for interacting with the ZhipuAI API.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(temperature=ZhiPuConstants.TEMPERATURE,
                         model=ZhiPuConstants.MODEL,
                         openai_api_key=ZhiPuConstants.OPENAI_API_KEY,
                         openai_api_base=ZhiPuConstants.OPENAI_API_BASE, **kwargs)
