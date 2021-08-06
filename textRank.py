# 針對每篇文章挑選出前4重要的句子做為參考
import networkx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import jieba
import csv

def readData(data_path):
    #預設欄位格式:標題/文章連結/內文/Hashtags/話題領域label
    title=[]
    href=[]
    context=[]
    hashtag=[]

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
    return context

class ExtractableAutomaticSummary:
    def __init__(self,article):
        """
        抽取式自动摘要
        :param article: 文章内容，列表，列表元素为字符串，包含了文章内容，形如['完整文章']
        :param num_sentences: 生成摘要的句子数
        """
        self.article = article
        self.stopwords = None
        self.word_embeddings = {}
        self.sentences_vectors = []
        self.ranked_sentences = None
        self.similarity_matrix = None
 
    def __get_sentences(self,sentences):
        """
        断句函数
        :param sentences:字符串，完整文章，在本例中，即为article[0]
        :return:列表，每个元素是一个字符串，字符串为一个句子
        """
        sentences = re.sub('([（），。！？\?])([^”’])', r"\1\n\2", sentences)  # 单字符断句符
        sentences = re.sub('(\.{6})([^”’])', r"\1\n\2", sentences)  # 英文省略号
        sentences = re.sub('(\…{2})([^”’])', r"\1\n\2", sentences)  # 中文省略号
        sentences = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', sentences)
        sentences = sentences.replace(' ', '\n')
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        sentences =sentences.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        return sentences.split("\n")

    def __get_stopwords(self):
        # 加载停用词，下载地址见最上注释
        self.stopwords = [line.strip() for line in open('./LSI/stopword.txt',encoding='utf-8').readlines()]

    def __remove_stopwords_from_sentence(self,sentence):
        # 去除停用词
        sentence = [i for i in sentence if i not in self.stopwords]
        return sentence

    def __get_word_embeddings(self):
        # 获取词向量，不要第一行，第一行是该词向量表的统计信息
        with open('wiki.zh.vector', encoding='utf-8') as f:
            lines = f.readlines()
            for _, line in enumerate(lines):
                if _ != 0:
                    values = line.split()
                    word = values[0]
                    coefs = np.asarray(values[1:], dtype='float32')
                    self.word_embeddings[word] = coefs

    def __get_sentence_vectors(self,cutted_clean_sentences):
        # 获取句向量，将句子中的每个词向量相加，再取均值，所得即为句向量
        for i in cutted_clean_sentences:
            if len(i) != 0:
                v = sum(
                    [self.word_embeddings.get(w.strip(), np.zeros((400,))) for w in i]
                ) / (len(i) + 1e-2)
            else:
                v = np.zeros((400,))
                # 因为预训练的词向量维度是400
            self.sentences_vectors.append(v)

    def __get_simlarity_matrix(self):
        # 计算相似度矩阵，基于余弦相似度
        self.similarity_matrix = np.zeros((len(self.sentences_vectors), len(self.sentences_vectors)))
        for i in range(len(self.sentences_vectors)):
            for j in range(len(self.sentences_vectors)):
                if i != j:
                    self.similarity_matrix[i][j] = cosine_similarity(
                        self.sentences_vectors[i].reshape(1, -1), self.sentences_vectors[j].reshape(1, -1)
                    )
                    # 这里reshape不可少
                    
    def calculate(self):
        self.__get_word_embeddings()
        # 获取词向量
        self.__get_stopwords()
        # 获取停用词
        sentences = self.__get_sentences(self.article)
#         sentences = self.__get_sentences(self.article[0])
#         for item in sentences:
#             print(item)
        # 将文章分割为句子
        userdict_path='CFG/CFG_dictionary.txt'
        jieba.load_userdict(userdict_path)
        cutted_sentences = [jieba.lcut(s) for s in sentences]
#         for item in cutted_sentences:
#             print(item)
        # 对每个句子分词
        cutted_clean_sentences = [self.__remove_stopwords_from_sentence(sentence) for sentence in cutted_sentences]
        # 句子分词后去停用词
        # 先分词，再去停用词，直接去停用词会把每个字分开，比如变成‘直 接 去 停 用 词 会 把 每 个 字 分 开’
        self.__get_sentence_vectors(cutted_clean_sentences)
        # 获取句向量
        self.__get_simlarity_matrix()
        # 获取相似度矩阵
        nx_graph = networkx.from_numpy_array(self.similarity_matrix)
        print(nx_graph)
        try:
            scores = networkx.pagerank(nx_graph,max_iter=800)
        except:
            scores = networkx.pagerank_numpy(nx_graph)
        # 将相似度矩阵转为图结构
        self.ranked_sentences = sorted(
            ((scores[i], s) for i, s in enumerate(sentences)), reverse=True
        )
        # 排序

    def get_abstract(self,num_abstract_sentences):
        # 这里的主函数将计算过程和获取得分前几的句子的函数分开，ranked_sentences写入类属性中，
        # 就可以重复调用get_abstract方法而避免多次计算了，方便测试
        with open ('CFG/Data/CFG_textRank.csv', 'a+', newline='',encoding = 'utf-8-sig') as csvFile:
             # build csvwriter
            writer = csv.writer(csvFile)
            # output content into csvfile
            print(num_abstract_sentences)
            if(len(self.ranked_sentences) < num_abstract_sentences):
                num_abstract_sentences = len(self.ranked_sentences)
            writer.writerow([self.ranked_sentences[i][1] for i in range(num_abstract_sentences)])
        for i in range(num_abstract_sentences):
            print(self.ranked_sentences[i][0])
            print(self.ranked_sentences[i][1])


# with open('測試文章.txt',encoding='utf-8') as f:
# 自己随手复制粘贴个文章进去即可
#     article = f.readlines()
articles = readData('CFG/Data/性別歧視.csv')
### test
# contend = articles[42]

# demo = ExtractableAutomaticSummary(contend)
# demo.calculate()
# demo.get_abstract(4)

for article in articles:
    demo = ExtractableAutomaticSummary(article)
    demo.calculate()
    demo.get_abstract(4)