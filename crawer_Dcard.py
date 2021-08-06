import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from tqdm import tqdm, trange
import random

import json
import csv
from fake_useragent import UserAgent

resp = []

def crawing_all_related_articles_multi(topic,epoch):
    
    title_list=[]
    total_href=[]
    articles_id=[]
    
    for j in range(epoch):
        url="https://www.dcard.tw/service/api/v2/search/posts?limit=100&query="+topic+"&offset="+str(i*100)
        reqs = requests.get(url)
        #use json.loads() to decode JSON
        reqsjson = json.loads(reqs.text)

        for i in range(100):
#             if len(reqsjson[i]['excerpt']) > 50:
                title_list.append(reqsjson[i]['title'])
                articles_id.append(reqsjson[i]['id'])
                #whatever you fill after "https://www.dcard.tw/f" ,it will run to correct pages based on your id 
                total_href.append('https://www.dcard.tw/f/mood/p/'+str(reqsjson[i]['id']))
                #print(title_list[i])
                #print(total_href[i])
                #print(articles_id[i])
            
    time.sleep(random.uniform(1, 5))
        
    return title_list,articles_id,total_href
def crawing_all_related_articles_multi_2(topic,epoch):
    
    title_list=[]
    total_href=[]
    articles_id=[]
    
    for i in range(epoch):
        word = str(i*epoch) + ' ~ ' + str((i+1)*epoch) +"\n"
        print(word)
        url="https://www.dcard.tw/service/api/v2/search/posts?limit="+str(epoch)+"&query="+topic+"&offset="+str(i*epoch)#+"&field=topics&sort=like&offset="+str(i)

        reqs = requests.get(url)
        #利用json.loads()解碼JSON
        reqsjson = json.loads(reqs.text)
        resp.append(reqsjson)
            
        time.sleep(1)
        
    for i in range(len(resp)):
        for j in range(epoch):
            title_list.append(resp[i][j]['title'])
            articles_id.append(resp[i][j]['id'])
            #whatever you fill after "https://www.dcard.tw/f" ,it will run to correct pages based on your id 
            total_href.append('https://www.dcard.tw/f/mood/p/'+str(resp[i][j]['id']))
            
    for k in range(len(resp)*epoch):
        print(title_list[k])
        print(total_href[k])
        print(articles_id[k])
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        
    return title_list,articles_id,total_href

def carwling_an_article_context(articles_id):
    lengh = len(articles_id)
    print('total:'+str(lengh)+' articles')
    print('=======================crawling the context=======================')
    context_list=[]
    hashtag_list=[]
    
    for i in range(lengh):
        try:
            url="https://www.dcard.tw/_api/posts/"+str(articles_id[i])
            ua = UserAgent()
            headers = {'User-Agent': ua.random}
            reqs = requests.get(url,headers= headers)
            #use json.loads() decode JSON
            reqsjson = json.loads(reqs.text)
            context = reqsjson['content']
            title = reqsjson['title']
            #print(i)
            #print(title)
            #print(context)
            
            #strip "\n" and some none-meaning space
            mseg_drop = context.strip().replace("\n", " ")
            msg_drop = mseg_drop.strip().replace("  ", " ")
            msg_drop = msg_drop.strip().replace("    ", " ")
            msg_drop = msg_drop.strip().replace("  ", " ")
            msg_drop= msg_drop.strip().replace("  ", " ")
            
            #print(msg_drop)
            
            context_list.append(msg_drop)

            hastags = reqsjson['topics']
            #print(hastags)
            
            msg=""

            for j in range(len(hastags)):
                if j!=len(hastags)-1:
                    msg = msg + hastags[j] + ','
                else:
                    msg = msg + hastags[j]

            hashtag_list.append(msg)
            print(hashtag_list)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

#             time.sleep(1)
            time.sleep(random.uniform(5, 10))
            #print('number'+str(i+1)+'article has already been crawled')
            
        except:
            #print(href_list[n])
            #print(n)
            context_list.append('NULL')
            hashtag_list.append('NULL')
            continue
            
    return context_list,hashtag_list

def save_csvfile(save_Path,save_Name,title_list,total_href,context_list,hashtag_list):
    with open (save_Path+save_Name+'.csv', 'a+', newline='',encoding = 'utf-8-sig') as csvFile:

        # build csvwriter
        writer = csv.writer(csvFile)

        writer.writerow(['title','href','context','hashtag'])

        # output content into csvfile
        for i in range(len(context_list)):
            writer.writerow([title_list[i],total_href[i],context_list[i],hashtag_list[i]])

    print('=======================finish crawling=======================')
    
    
if __name__ == '__main__':
    
    topic = "性別歧視"
    save_Path = "./CFG/"
    save_Name = topic

#     title_list,articles_id,total_href = crawing_all_related_articles_multi(topic,1)
    title_list,articles_id,total_href = crawing_all_related_articles_multi_2(topic,10)

    context_list,hastag_list = carwling_an_article_context(articles_id[:50])
    save_csvfile(save_Path,save_Name,title_list,total_href,context_list,hastag_list)