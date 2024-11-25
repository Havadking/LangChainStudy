from __future__ import annotations

import logging
from typing import Dict, List, Any

from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, root_validator
from pydantic import model_validator

logger = logging.getLogger(__name__)

class ZhipuAIEmbeddings(BaseModel, Embeddings):
    """ZhipuAI embedding models.
    Example:
       .. code-block:: python
            from langchain.embeddings import ZhipuAIEmbeddings
            embeddings = ZhipuAIEmbeddings()
    """
    client: Any  #: :meta private:

    # @model_validator(mode="after")
    # def validate_environment(cls, values: Dict) -> Dict:
    #     """
    #     实例化ZhipuAI为values["client"]
    #
    #     Args:
    #
    #         values (Dict): 包含配置信息的字典，必须包含 client 的字段.
    #     Returns:
    #
    #         values (Dict): 包含配置信息的字典。如果环境中有zhipuai库，则将返回实例化的ZhipuAI类；否则将报错 'ModuleNotFoundError: No module named 'zhipuai''.
    #     """
    #     from zhipuai import ZhipuAI
    #     values["client"] = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")
    #     return values


    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
            生成输入文本列表的 embedding.
            Args:
                texts (List[str]): 要生成 embedding 的文本列表.

            Returns:
                List[List[float]]: 输入列表中每个文档的 embedding 列表。每个 embedding 都表示为一个浮点值列表。
            """
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """
            生成输入文本的 embedding.

            Args:
                text (str): 要生成 embedding 的文本.

            Return:
                embeddings (List[float]): 输入文本的 embedding，一个浮点数值列表.
            """
        embeddings = self.client.embeddings.create(
            model="embedding-3",
            input=text
        )
        return embeddings.data[0].embedding

