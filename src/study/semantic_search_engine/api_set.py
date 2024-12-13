import getpass
import os

if not os.getenv("ZHIPUAI_API_KEY"):
    os.environ["ZHIPUAI_API_KEY"] = getpass.getpass("Enter your ZhipuAI API key: ")