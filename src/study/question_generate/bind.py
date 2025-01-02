import pandas as pd
import requests


def get_paper_ids(paper_name):
    url = "http://rest.xxt.cn/xinzx-resource/paper/get-paper-list"
    headers = {
        "Cookie": "xxtSessionId=a3264da3ed08aacd4f09ec95596f4a2fa0ba38e3; NTKF_T2D_CLIENTID=guest12A1A814-5FEB-36A9-4F91-C00D5EEBAAA2; _did__=173318548641390918921580602477062; nTalk_CACHE_DATA={uid:kf_9115_ISME9754_guest12A1A814-5FEB-36,tid:1735005996705473}; schoolOrderGuide={%22province%22:1%2C%22isHbLT%22:false%2C%22isHbYD%22:false%2C%22guideOrderInSzjx%22:true%2C%22webId%22:%222319877%22}; XXT_ID=34013848; _XXT_ID=34013848; _LOGIN_MA_=lw%2d34017212%23ma%2dt%23rce%2df; XXT_TICKET=73cd7908dd124b524c59466a8039cd36850baa9e; _XSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _SSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _TSVID__=a2448a172c1145a9bbf0eddde2c2252c; _bgid__=as9ufsmPaY02D4elPbkYDfVwp95pUlZ1yPCmWjPPqc4RLybNrKvCJz666AaY2McE; sidebarStatus=0",
        # 替换为实际的Cookie
        "Content-Type": "application/json"
    }
    data = {
        "search": {
            "accessSource": 900,
            "paperName": paper_name
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 如果状态码不是200，抛出HTTPError

        result = response.json()

        if "resultList" in result and result["resultList"]:
            return result["resultList"][0]["paperId"]
            # paper_ids = [item["paperId"] for item in result["resultList"]]
            # return paper_ids
        else:
            print("查询失败：未找到相关结果。")
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def get_book_id(book_name):
    url = "http://rest.xxt.cn/xinzx-resource/bg-book-catalog/get-book-list-by-filter"
    headers = {
        "Cookie": "xxtSessionId=a3264da3ed08aacd4f09ec95596f4a2fa0ba38e3; NTKF_T2D_CLIENTID=guest12A1A814-5FEB-36A9-4F91-C00D5EEBAAA2; _did__=173318548641390918921580602477062; nTalk_CACHE_DATA={uid:kf_9115_ISME9754_guest12A1A814-5FEB-36,tid:1735005996705473}; schoolOrderGuide={%22province%22:1%2C%22isHbLT%22:false%2C%22isHbYD%22:false%2C%22guideOrderInSzjx%22:true%2C%22webId%22:%222319877%22}; XXT_ID=34013848; _XXT_ID=34013848; _LOGIN_MA_=lw%2d34017212%23ma%2dt%23rce%2df; XXT_TICKET=73cd7908dd124b524c59466a8039cd36850baa9e; _XSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _SSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _TSVID__=a2448a172c1145a9bbf0eddde2c2252c; _bgid__=as9ufsmPaY02D4elPbkYDfVwp95pUlZ1yPCmWjPPqc4RLybNrKvCJz666AaY2McE; sidebarStatus=0",
        # 替换为实际的Cookie
        "Content-Type": "application/json"
    }
    data = {
        "search": {
            "bookType": 2,
            "bookName": book_name
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 如果状态码不是200，抛出HTTPError

        result = response.json()

        if "resultList" in result and result["resultList"]:
            return result["resultList"][0]["bookId"]
            # book_ids = [item["bookId"] for item in result["resultList"]]
            # return book_ids
        else:
            print("查询失败：未找到相关结果。")
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def sync_books(query_data):
    url = "http://rest.xxt.cn/xinzx-resource/bg-book-catalog/add-isbn-book"
    headers = {
        "Cookie": "xxtSessionId=a3264da3ed08aacd4f09ec95596f4a2fa0ba38e3; NTKF_T2D_CLIENTID=guest12A1A814-5FEB-36A9-4F91-C00D5EEBAAA2; _did__=173318548641390918921580602477062; nTalk_CACHE_DATA={uid:kf_9115_ISME9754_guest12A1A814-5FEB-36,tid:1735005996705473}; schoolOrderGuide={%22province%22:1%2C%22isHbLT%22:false%2C%22isHbYD%22:false%2C%22guideOrderInSzjx%22:true%2C%22webId%22:%222319877%22}; XXT_ID=34013848; _XXT_ID=34013848; _LOGIN_MA_=lw%2d34017212%23ma%2dt%23rce%2df; XXT_TICKET=73cd7908dd124b524c59466a8039cd36850baa9e; _XSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _SSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _TSVID__=a2448a172c1145a9bbf0eddde2c2252c; _bgid__=as9ufsmPaY02D4elPbkYDfVwp95pUlZ1yPCmWjPPqc4RLybNrKvCJz666AaY2McE; sidebarStatus=0",
        # 替换为实际的Cookie
        "Content-Type": "application/json"
    }
    # data = [
    #     {
    #         "isbn": "9787514709155",
    #         "bookName": "中华人物故事汇.中华先烈人物故事汇",
    #         "imageUrl": "http://static.tanshuapi.com/isbn/202343/169806619868f123.jpg"
    #     },
    #     {
    #         "isbn": "9787547744116",
    #         "bookName": "写给孩子的哲学启蒙书",
    #         "imageUrl": "http://static.tanshuapi.com/isbn/202429/17213766273021ea.jpg"
    #     }
    # ]
    data = query_data

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 如果状态码不是200，抛出HTTPError

        result = response.json()
        print(f"result is {result}")

        # if "resultList" in result and result["resultList"]:
        #     return result["resultList"][0]["bookId"]
        #     # book_ids = [item["bookId"] for item in result["resultList"]]
        #     # return book_ids
        # else:
        #     print("查询失败：未找到相关结果。")
        #     return None

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def bind_paper_2_book(book_id, paper_id):
    url = "http://rest.xxt.cn/xinzx-resource/bg-book-catalog/save-book-catalog-paper-rel"
    headers = {
        "Cookie": "xxtSessionId=a3264da3ed08aacd4f09ec95596f4a2fa0ba38e3; NTKF_T2D_CLIENTID=guest12A1A814-5FEB-36A9-4F91-C00D5EEBAAA2; _did__=173318548641390918921580602477062; nTalk_CACHE_DATA={uid:kf_9115_ISME9754_guest12A1A814-5FEB-36,tid:1735005996705473}; schoolOrderGuide={%22province%22:1%2C%22isHbLT%22:false%2C%22isHbYD%22:false%2C%22guideOrderInSzjx%22:true%2C%22webId%22:%222319877%22}; XXT_ID=34013848; _XXT_ID=34013848; _LOGIN_MA_=lw%2d34017212%23ma%2dt%23rce%2df; XXT_TICKET=73cd7908dd124b524c59466a8039cd36850baa9e; _XSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _SSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _TSVID__=a2448a172c1145a9bbf0eddde2c2252c; _bgid__=as9ufsmPaY02D4elPbkYDfVwp95pUlZ1yPCmWjPPqc4RLybNrKvCJz666AaY2McE; sidebarStatus=0",
        # 替换为实际的Cookie
        "Content-Type": "application/json"
    }
    data = {
        "bookId": book_id,
        "paperId": paper_id,
        "applicationType": 6,
        "relStatus": 1
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 如果状态码不是200，抛出HTTPError

        result = response.json()
        print(f"result is {result}")

        # if "resultList" in result and result["resultList"]:
        #     return result["resultList"][0]["bookId"]
        #     # book_ids = [item["bookId"] for item in result["resultList"]]
        #     # return book_ids
        # else:
        #     print("查询失败：未找到相关结果。")
        #     return None

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        print(book_id)
        return None


# paper_name = "德伯家的苔丝"
# paper_ids = get_paper_ids(paper_name)
#
# if paper_ids:
#     print(f"查询成功，Paper IDs: {paper_ids}")
# else:
#     print("查询失败。")
#
# book_name = "秘密花园"
# book_ids = get_book_id(book_name)
#
# if book_ids:
#     print(f"查询成功，Book IDs: {book_ids}")
# else:
#     print("查询失败。")

# sync_books()

def find_bind(book):
    paper_ids = get_paper_ids(book)
    if paper_ids:
        print(f"查询成功，Paper IDs: {paper_ids}")
    else:
        print("查询失败。")
    book_ids = get_book_id(book)
    if book_ids:
        print(f"查询成功，Book IDs: {book_ids}")
    else:
        print("查询失败。")
    bind_paper_2_book(book_ids, paper_id=paper_ids)


if __name__ == '__main__':
    # book = "写给孩子的哲学启蒙书"
    # find_bind(book)
    # 假设你的 Excel 文件名为 books.xlsx，且 Sheet 名为 Sheet1
    file_path = '/Users/macmini/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/AFE4FE3B7A8CC8C32782E06AA8AD618A/Caches/Files/2025-01/50417b9b7fdeb96d23e2b8b753bcfdb1/导入书籍.xlsx'
    df = pd.read_excel(file_path)
    #
    # # 将每一行转为字典格式并加入列表
    # data = [
    #     {
    #         "isbn": str(row["isbn"]),  # 确保 ISBN 是字符串
    #         "bookName": str(row["图书名字"]),  # 确保图书名称是字符串
    #         "imageUrl": str(row["封面地址url"])  # 确保封面地址是字符串
    #     }
    #     for _, row in df.iterrows()
    # ]
    #
    # # 打印结果
    # print(data)
    # sync_books(query_data=data)
    # 获取图书名称为字符串列表
    book_names = df["图书名字"].dropna().tolist()

    # 循环打印每个图书名称
    for name in book_names:
        print(f'开始绑定{name}---------------')
        find_bind(name)
        print("-------------------------------")

