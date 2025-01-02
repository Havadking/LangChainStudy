import json
import os
import time
from typing import List

import requests
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.model.DeepSeekAILLM import DeepSeekAILLM
from src.model.DouBaoAILLM import DouBaoAILLM
from src.study.question_generate.json2word import create_docx


# 定义输出的格式
class Question(BaseModel):
    """question of the book."""
    question: str = Field(description="问题")
    options: List[str] = Field(description="该问题的四个选项，格式为：'A．选项的内容' ")
    answer: str = Field(description="问题的答案", examples=["A", "B", "C", "D"])


class Knowledge(BaseModel):
    """classify question by knowledge"""
    knowledge: str = Field(description="问题的分类",
                           examples=["语言运用", "修辞鉴赏", "内容理解", "主题思想", "文化常识"])
    questions: List[Question] = Field(description="问题的集合")


class Questions(BaseModel):
    """A collection of some questions"""
    questions: List[Knowledge] = Field(description="根据知识点分类的问题的集合")


# 定义输出解释器
parser = PydanticOutputParser(pydantic_object=Questions)
# 定义提示词和所需参数
prompt = PromptTemplate(
    template="""
    你是一位资深的教育内容设计专家，结合中国考试中相关可能的知识点，专注于为不同学习阶段设计高质量的选择题。请根据以下要求生成选择题：
    根据书名 {book} 的内容，设计与书本相关的选择题。
    选择题需要覆盖整本书的主要内容，包括但不限于故事情节、主题思想、人物特征、重要场景和核心概念，尽量减少出现猜人物的问题。
    按照严格的 JSON 格式生成10道选择题，每题包含4个选项，其中只有1个正确答案，其他3个为具有一定迷惑性的错误答案。
    题目分为5个知识点（语言运用、修辞鉴赏、内容理解、主题思想、文化常识），每个知识点生成2道题目。
    选项设置需符合 {carer} 学生的理解能力（小学、初中、高中），并确保问题和答案语言表达清晰、简洁。
    保持题目的趣味性和互动性，避免过于晦涩难懂。
    题目内容需完全基于书籍内容。
    适用阶段的知识范围和语言风格需要严格符合指定阶段。
    
    生成的每个选择题必须严格的包括一下的字段：
        - question（问题）：问题的描述
        - options（选项）：该问题的选项，包括A、B、C、D是个选项，格式为：'A．选项的内容'
        - answer（答案）：该问题的正确答案
        - knowledge（知识点）：该问题属于那个知识点，包括：语言运用、修辞鉴赏、内容理解、主题思想、文化常识

    输出格式：{format_instructions}

    """,
    input_variables=["book", "carer", ],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
# 定义大模型
# llm = ZhipuAILLM()
# llm = DouBaoAILLM()
llm = DeepSeekAILLM()
# llm = ChatOpenAI(
#     temperature=0.1,
#     openai_api_key="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",
#     openai_api_base="https://openrouter.ai/api/v1",
#     model="google/gemini-2.0-flash-exp:free"
# )

# 组装成链
chain = prompt | llm | parser


# chain = chain.bind(callback_manager=callback_manager, verbose=True)

def generateQuestions(book: str, num: int, carer: str):
    print(f"开始生成《{book}》相关的题目")
    with get_openai_callback() as cb:
        output = chain.invoke(
            {
                "book": book,
                "carer": carer,
            }
        )
        print(cb)

    # print(output.usage_metadata)
    # 定义 JSON 文件的路径
    json_file_path = os.path.abspath(book + ".json")

    output_dict = output.dict()
    # handler = callback_manager.handlers[0]
    # print(f"Prompt Tokens: {handler.prompt_tokens}")
    # print(f"Completion Tokens: {handler.completion_tokens}")
    # print(f"Total Tokens: {handler.total_tokens}")
    # print(f"Execution Time (s): {handler.execution_time}")

    # print(output_dict)

    # 保存为 JSON 文件
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(output_dict, json_file, ensure_ascii=False, indent=4)

    print(f"成功生成{num}个《{book}》相关的题目")

    # 返回生成的 JSON 文件的绝对路径
    return json_file_path


def upload_word_file(file_path, cookie):
    """
    Upload a Word file to the specified API using a Multipart Form.

    Parameters:
        file_path (str): The local path to the Word file to upload.
        cookie (str): The cookie for authentication.

    Returns:
        response (requests.Response): The response from the API.
    """
    url = "http://rest.xxt.cn/zuul/xinzx-resource/paper-ingestion/upload-attachments"
    headers = {
        "Cookie": cookie  # Include the provided cookie in the request headers.
    }

    # Open the file in binary mode for upload.
    with open(file_path, "rb") as file:
        files = {"file": (
        file_path.split("/")[-1], file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}

        try:
            response = requests.post(url, headers=headers, files=files)

            # Raise an HTTPError if the response indicates a failed request.
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None


def upload_paper(file_identity, cookie):
    """
    Upload paper metadata to the specified API.

    Parameters:
        file_identity (str): The file identity returned from the previous upload.
        cookie (str): The cookie for authentication.

    Returns:
        response (requests.Response): The response from the API.
    """
    url = "http://rest.xxt.cn/xinzx-resource/paper-ingestion/paper-upload"
    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json"
    }

    data = {
        "phaseCode": 311,
        "subjectCode": 13,
        "paperType": 6,
        "versionCode": [17],
        "gradeCode": 31,
        "termCode": 1,
        "paperSource": 900,
        "paperPrivateInfos": [
            {
                "provinceCode": 1,
                "cityCode": 371,
                "year": 2024,
                "etestMark": "AI自动生成",
                "paperSeq": 1
            }
        ],
        "tags": [],
        "paperClassification": "1",
        "quality": 0,
        "fileIdentity": file_identity
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        # Raise an HTTPError if the response indicates a failed request.
        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def generate_upload_paper(book: str):
    json_path = generateQuestions(book, 10, "高中")
    print(f"Json is in {json_path}")
    book_name = '《' + book + '》'
    file_path = create_docx(json_path, book_name)
    print(f"Docx is in {file_path}")
    # file_path = "/Users/macmini/Documents/题目/《战争与和平》名著测试题.docx"  # Replace with the path to your Word file.
    cookie = "xxtSessionId=a3264da3ed08aacd4f09ec95596f4a2fa0ba38e3; NTKF_T2D_CLIENTID=guest12A1A814-5FEB-36A9-4F91-C00D5EEBAAA2; _did__=173318548641390918921580602477062; nTalk_CACHE_DATA={uid:kf_9115_ISME9754_guest12A1A814-5FEB-36,tid:1735005996705473}; schoolOrderGuide={%22province%22:1%2C%22isHbLT%22:false%2C%22isHbYD%22:false%2C%22guideOrderInSzjx%22:true%2C%22webId%22:%222319877%22}; XXT_ID=34013848; _XXT_ID=34013848; _LOGIN_MA_=lw%2d34017212%23ma%2dt%23rce%2df; XXT_TICKET=73cd7908dd124b524c59466a8039cd36850baa9e; _XSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _SSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _TSVID__=a2448a172c1145a9bbf0eddde2c2252c; _bgid__=as9ufsmPaY02D4elPbkYDfVwp95pUlZ1yPCmWjPPqc4RLybNrKvCJz666AaY2McE; sidebarStatus=0"  # Replace with your authentication cookie.
    # 上传附件
    response = upload_word_file(file_path, cookie)
    if response:
        print("Upload successful! Response:")
        print(response.json().get("fileIdentity"))  # Assuming the API returns a JSON response.
        file_identity = response.json().get("fileIdentity")

        # 上传试卷
        paper_response = upload_paper(file_identity, cookie)
        if paper_response:
            print("Paper uploaded successfully! Response:")
            print(paper_response.json())
        else:
            print("Failed to upload paper metadata.")
    else:
        print("Upload failed.")


if __name__ == '__main__':

    book = "少年音乐和美术故事"
    start_time = time.time()
    generate_upload_paper(book=book)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
