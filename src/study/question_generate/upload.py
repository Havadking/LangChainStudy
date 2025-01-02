import os

from src.study.question_generate.book_question import upload_word_file, upload_paper


def list_files_with_absolute_path(folder_path):
    try:
        # 遍历文件夹中的所有文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                # 获取文件的绝对路径
                absolute_path = os.path.join(root, file)
                print(absolute_path)
                cookie = "xxtSessionId=a3264da3ed08aacd4f09ec95596f4a2fa0ba38e3; NTKF_T2D_CLIENTID=guest12A1A814-5FEB-36A9-4F91-C00D5EEBAAA2; _did__=173318548641390918921580602477062; nTalk_CACHE_DATA={uid:kf_9115_ISME9754_guest12A1A814-5FEB-36,tid:1735005996705473}; schoolOrderGuide={%22province%22:1%2C%22isHbLT%22:false%2C%22isHbYD%22:false%2C%22guideOrderInSzjx%22:true%2C%22webId%22:%222319877%22}; XXT_ID=34013848; _XXT_ID=34013848; _LOGIN_MA_=lw%2d34017212%23ma%2dt%23rce%2df; XXT_TICKET=73cd7908dd124b524c59466a8039cd36850baa9e; _XSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _SSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _TSVID__=9b9a79ff7b35407189dc92f1804d565a; _bgid__=tZkHwrNvQKG1QUBWPezmp4vmGMse0NdCrLzKvzAZPMZAUzlFNuMEwYYZX2c4BUVV; sidebarStatus=0"
                # cookie = "_did__=17152487570069092678608235675821; xxtSessionId=a3264da3ed08aacd4f09ec95596f4a2fa0ba38e3; NTKF_T2D_CLIENTID=guest12A1A814-5FEB-36A9-4F91-C00D5EEBAAA2; nTalk_CACHE_DATA={uid:kf_9115_ISME9754_guest12A1A814-5FEB-36,tid:1735005996705473}; schoolOrderGuide={%22province%22:1%2C%22isHbLT%22:false%2C%22isHbYD%22:false%2C%22guideOrderInSzjx%22:true%2C%22webId%22:%222319877%22}; XXT_ID=34013848; _XXT_ID=34013848; _LOGIN_MA_=lw%2d34017212%23ma%2dt%23rce%2df; XXT_TICKET=73cd7908dd124b524c59466a8039cd36850baa9e; _XSID_=73cd7908dd124b524c59466a8039cd36850baa9e; _SSID_=73cd7908dd124b524c59466a8039cd36850baa9e; sidebarStatus=0; _bgid__=dwLhxFvHYmGv5egTtQvGnymu0bA7Qha4tEfdGjtd6JVtGs942P3AXEpj8Zz8hKAB"
                # 上传附件
                response = upload_word_file(absolute_path, cookie)
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



    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例
if __name__ == '__main__':
    folder_path = "/Users/macmini/Documents/题目生成"
    list_files_with_absolute_path(folder_path)


