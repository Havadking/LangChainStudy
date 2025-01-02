import time

import pandas as pd

from src.study.question_generate.book_question import generate_upload_paper

# 读取 Excel 文件
file_path = '/Users/macmini/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/AFE4FE3B7A8CC8C32782E06AA8AD618A/Caches/Files/2025-01/50417b9b7fdeb96d23e2b8b753bcfdb1/导入书籍.xlsx'  # 替换为你的 Excel 文件路径
sheet_name = '导入书籍'  # 替换为你的工作表名称（如果不是默认的 Sheet1）

# 加载 Excel 文件
df = pd.read_excel(file_path, sheet_name=sheet_name)

# 提取 "书名" 列的前 50 个数据
# 彩色的梦 轻叩诗歌大门
# top_50_books = df['书名'].head(50)
top_50_books = df['图书名字'].iloc[43:]

# 循环输出书名
for index, book in enumerate(top_50_books, start=1):
    print(f"{index}. {book}")
    start_time = time.time()
    generate_upload_paper(book=book)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
