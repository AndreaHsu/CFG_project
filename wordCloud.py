import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba
import numpy as np
import csv
import matplotlib.font_manager as fm

import matplotlib
print(matplotlib.__file__)

#### 將挑選字詞取出做成CGF_dictionary.txt
words= []
with open("挑詞.csv",newline='',encoding="utf" ,errors='ignore') as f:
    rows = csv.reader(f)
    for row in rows:
        words.append(row)
        
for item in words:
    print(item)
    
with open('CFG_dictionary.txt', 'w+', newline='',encoding = 'utf-8-sig') as csvFile:
    writer = csv.writer(csvFile)
    for word in words:
        writer.writerow(word)
        
# 引入中文字體
fontPath = r'C:\Users\user\Downloads\NotoSansCJKtc-hinted\NotoSansCJKtc-Regular.otf'

#### 特定領域產生文字雲
context = ""
with open("Data/言語性騷擾.dataset",encoding='utf',newline='') as f:
    rows = csv.DictReader(f)
    for row in rows:
        context += ' '.join(row)
    
wc = WordCloud(
    background_color='white',  # 設置背景顏色
    font_path =fontPath,
    max_words=200,  # 設置最大字數
    stopwords={'支持','還會性','活摘','防疫','新聞','耐心','仔細','誠心','建議','人','發表言論'},  # 設置停用词
#     max_font_size=150,  # 設置字體最大值
    random_state=1,  # 設置有多少種隨機生成狀態，即為幾種配色方案
    width=2000, height=1200
)
 # 輸入文本
wc.generate(context)

plt.imshow(wc.recolor())
 
 # 隱藏圖像座標軸
plt.axis("off")
plt.show()
# 保存圖片
wc.to_file('.jpg')

#### 總文字雲產生
text = open("CFG_dictionary.txt",encoding = 'utf').read()
# 設定停用字(排除常用詞、無法代表特殊意義的字詞)
stopwords = {}.fromkeys(["沒有","落伍","魯肥宅","廢物","是不是男人","性別歧視","親子廁所放在殘障樓層"])
# 產生文字雲
wc = WordCloud(font_path=fontPath, #設置字體
               background_color="white", #背景顏色
               max_words = 100 ,        #文字雲顯示最大詞數
               stopwords=stopwords,
               width=2000, height=1200)  #停用字詞
wc.generate(text)
# 視覺化呈現
plt.imshow(wc)
plt.axis("off")
plt.figure(figsize=(20,10), dpi = 100)
plt.show()

wc.to_file('CFG.jpg')