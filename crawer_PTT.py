# 導入 模組(module) 
import requests 
import json
# 導入 BeautifulSoup 模組(module)：解析HTML 語法工具
import bs4
import csv
import time


def craw_href(search):
    href_list = []
    for page in range(5):
        page = page+1
        # 把 到 ptt 八卦版 網址存到URL 變數中
        URL = "https://www.ptt.cc/bbs/Gossiping/search?page="+str(page)+"&q="+search
        # 設定Header與Cookie
        my_headers = {'cookie': 'over18=1;'}
        # 發送get 請求 到 ptt 八卦版
        response = requests.get(URL, headers = my_headers)
        # 印出回傳網頁程式碼

        # print(response.text)


        # 導入 BeautifulSoup 模組(module)：解析HTML 語法工具
        import bs4

        # 2-1 把網頁程式碼(HTML) 丟入 bs4模組分析
        soup = bs4.BeautifulSoup(response.text,"html.parser")

        '''
        <div class="title"> 
            <a href="/bbs/Gossiping/M.1589705973.A.912.html">
              [問卦] 為什麼八卦的民意在社會上都體現不出來呢
            </a>	
        </div>
        '''
        # 2-2 查找所有html 元素 過濾出 標籤名稱為 'div' 同時class為 title 
        titles = soup.find_all('div','title')
        hrefs = soup.select('.title a')

        for i in range(len(hrefs)):
            href_list.append(hrefs[i]['href'])

#         print(href_list)

        # 2-3 萃取文字出來。
        # 因為我們有多個Tags存放在 List titles中。
        # 所以需要使用for 迴圈將逐筆將List 
        for t in titles:
            print(t.text)
    
    return href_list

def craw_content(href_list):
    basicUrl = "https://www.ptt.cc"
    url = ""
    title_list = []
    content_list = []
    url_list = []
    for item in href_list:
        url = basicUrl+item
        print(url)
        url_list.append(url)
        response = requests.get(url, headers = my_headers)
        #  把網頁程式碼(HTML) 丟入 bs4模組分析
        soup = bs4.BeautifulSoup(response.text,"html.parser")

        ## PTT 上方4個欄位
        header = soup.find_all('span','article-meta-value')

        # 作者
#         author = header[0].text
#         # 看版
#         board = header[1].text
        # 標題
        title = header[2].text
        # 日期
#         date = header[3].text


        ## 查找所有html 元素 抓出內容
        main_container = soup.find(id='main-container')
        # 把所有文字都抓出來
        all_text = main_container.text
        # 把整個內容切割透過 "-- " 切割成2個陣列
        pre_text = all_text.split('--')[0]

        # 把每段文字 根據 '\n' 切開
        texts = pre_text.split('\n')
        # 如果你爬多篇你會發現 
        contents = texts[2:]
        # 內容
        content = '\n'.join(contents)


        # 顯示
#         print('作者：'+author)
#         print('看板：'+board)
#         print('標題：'+title)
#         print('日期：'+date)
#         print('內容：'+content)

        title_list.append(title)
        content_list.append(content)
        time.sleep(1)
    return title_list,content_list,url_list

def save_csvfile(save_Path,save_Name,title_list,url_list,context_list):
    with open (save_Path+save_Name+'ptt.csv', 'a+', newline='',encoding = 'utf-8-sig') as csvFile:

        # build csvwriter
        writer = csv.writer(csvFile)

        writer.writerow(['title','href','context'])

        # output content into csvfile
        for i in range(len(title_list)):
            writer.writerow([title_list[i],url_list[i],context_list[i]])

    print('=======================finish crawling=======================')
    

if __name__ == '__main__':
    
    search = "言語性霸凌"
    save_Path = "./CFG/Data/"
    save_Name = search

    total_href = craw_href(search)

    title_list,context_list,url_list = craw_content(total_href)
    save_csvfile(save_Path,save_Name,title_list,url_list,context_list)