#Import相關資源
import matplotlib.pyplot as plt
import numpy as np
import jieba.analyse
import jieba
#import codecs0
import codecs

# see logging events
import logging
logging.disable(50)
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import os
from gensim import corpora, models, similarities
#from six import iteritems

import re
jieba.case_sensitive = True # 可控制對於詞彙中的英文部分是否為case sensitive, 預設False

import csv
from tqdm import tqdm, trange

#讀取訓練資料
def readData(data_path):
    #預設欄位格式:標題/文章連結/內文/Hashtags/話題領域label
    title=[]
    href=[]
    context=[]
    hashtag=[]
    #label=[]
    jieba.load_userdict(userdict_path)

    # 開啟 CSV 檔案
    with open(data_path, newline='',encoding = 'utf-8-sig') as csvFile:

      # 3.轉成一個 dictionary, 讀取 CSV 檔內容，將每一列轉成字典
      rows = csv.DictReader(csvFile)

      # 迴圈輸出 指定欄位
      for row in rows:
            title.append(row['title'])
            context.append(row['context'])
            href.append(row['href'])
            hashtag.append(row['hashtag'])

    return title,href,context,hashtag

#Jieba斷詞及去除停用字
def jiebaAndStopword(context,userdict_path,stopword_path,save_path):
    #jieba斷詞
    for i in range(len(context)):
        remove_msg = re.sub('[(%。，》／：…？/」▲※▼▲★●【｜】◎:&\'-.『』！!-〈〉‘’\n（）「；～＆ㄜ〰🔴🙂🤮🈶🤓🤧👏😯👆🌚😥😃🥴🌝😜😝😨🖐👌😁👼👻－👵👿📖🔆😮🌟🏭👎👈😳😇😣😁😖😩😫😙😞🤗🙂🤨🔔🤩😦🤮😇💡🙋🧐😁💜🤕😰👨🎉🎉👋💻🚀📢🐣🚩👀🔹🔸🔺🙇😟😬🐶🤯🤬🤪😍👧💁👊😱🔥🙂😣🤤🤫😥📌📍🐳😟😨😠👏😾🤫👉👇😑😆😂😄😱👿👌🙇🤵😟🧐～🙏👍💪🙄🙃😒👂😭😡🤦😢😅😀😭🌸😊🤔😊😏😔😐💥🐦💦😵😓😡💸🥺🤷🤦🤣🥳💩💢🤢👩🏻👩😧🔪😤💰😎😚🤭💝💞💓🥰💗💘🤝🍀🔻🎈🔎🙂👆🎓👣🗣🤳🙋🌀👥🙇)(a-zA-Z))]',"",context[i])
        seg_list = jieba.cut(remove_msg)
        final_msg = " ".join(seg_list)
        msg_drop = final_msg.strip().replace("  ", " ")
        msg_drop = msg_drop.strip().replace("    ", " ")
        msg_drop = msg_drop.strip().replace("  ", " ")
        final_msg= msg_drop.strip().replace("  ", " ")
        context[i] = final_msg
        
    #去除停用字
    #載入停用詞字典
    f = open(stopword_path,encoding = 'utf-8-sig')
    stoplist = f.readlines()
    f.close()

    for i in range(len(stoplist)):
        stoplist[i] = re.sub('\n',"",stoplist[i])
        
    for i in tqdm(range(len(context))):
        #開始消除停用字
        content = context[i].split(' ')
        del_context=[]
        for word in range(len(content)):
            for j in range(len(stoplist)):
                if content[word] == stoplist[j]:
                    del_context.append(stoplist[j])

        #print("去除單詞:")
        #print(del_context)

        for k in range(len(del_context)):
            try:
                content.remove(del_context[k])
            except:
                print("",end="")
                #print(del_context[k]+":已刪除")

        #去除相同單詞
        temp = list(set(content))
        #恢復原本排列
        content= sorted(temp,key=content.index)
        
        #刪除一個字獨立成一詞的
        del_single_word=[]
        for l in range(len(content)):
            if len(content[l])<2:
                del_single_word.append(content[l])

        for n in range(len(del_single_word)):
            try:
                content.remove(del_single_word[n])
            except:
                print("",end="")

        #去除相同單詞
        temp = list(set(content))
        #恢復原本排列
        content = sorted(temp,key=content.index)

        current_msg=""
        for m in range(len(content)):
            if m!=len(content)-1:
                current_msg = current_msg + content[m] + " "
            else:
                current_msg = current_msg + content[m]
        ##
        context[i] = current_msg
        
        with open(save_path+'\\性別歧視ptt.dataset', 'w+', newline='',encoding = 'utf-8-sig') as csvFile:
            # 建立 CSV 檔寫入器
            writer = csv.writer(csvFile)
            for i in range(len(context)):
                writer.writerow([context[i]])
                
if __name__ === "__main__":
    
    #訓練資料的路徑
    data_path='.\\CFG\\Data\\性別歧視ptt.csv'
    #自定義的斷詞字典路徑
    userdict_path='.\\LSI\\userDict.txt'
    #停用字字典路徑
    stopword_path='.\\LSI\\stopword.txt'
    #模型存放路徑
    save_path='.\\CFG\\Data\\'

    print('#--讀取訓練資料--#')
    title,href,context,hashtag = readData(data_path)
    #print(context)
    print('#--進行資料前處理--#')
    jiebaAndStopword(context,userdict_path,stopword_path,save_path)