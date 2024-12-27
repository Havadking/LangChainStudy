from typing import List, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.xxt_ai_chat.xxt_common.llm.zhipu_llm import ZhipuAILLM

# 定义 Pydantic 模型来描述 JSON 结构
class StoryPart(BaseModel):
    background: str = Field(description="背景描述")
    dialog: List[str] = Field(description="对话内容", default_factory=list)
    narration: Optional[str] = Field(description="旁白", default=None)


class StoryCollection(BaseModel):
    stories: List[StoryPart] = Field(description="故事片段集合")


class ScriptCreator:
    def __init__(self):
        self.llm = ZhipuAILLM()
        # 创建输出解析器
        self.parser = PydanticOutputParser(pydantic_object=StoryCollection)
        self.prompt = PromptTemplate(
    template="""根据下列提到的故事的内容，按照严格的 JSON 格式生成{num_stories}个儿童故事片段。
    要求:剧本简洁但完整的讲完这个故事，对话衔接合理。
    
    每个片段必须包含：
        - background（背景）：描述故事发生的场景,目的是用于生成背景图片，不要包含说话等图片无法描述的动态因素
        - dialog（对话）：包含人物对话的列表,格式为“人物名字（人物心理或表情） + `说:` +对话内容”
        - narration（旁白）：描述故事情节或人物心理，推进故事的发展

    输出格式：{format_instructions}

    故事内容：{content}
""",
    input_variables=["content", "num_stories"],
    partial_variables={"format_instructions":self.parser.get_format_instructions()}
)
        self.chain =  self.prompt | self.llm | self.parser


    def create_script(self, story, num_stories=4):
        """
        生成剧本
        """
        script = self.chain.invoke(
            {
                "content": story,
                "num_stories": num_stories
            }
        )
        return script

