import pandas as pd
from wordcloud import WordCloud
import jieba
import PIL.Image as image
import numpy
import re

def my_cloud(data):
    text=''
    for word in data:
        text+=str(word)
    text=re.sub(r'[0-9a-zA-z]*','',text)
    text_list=jieba.cut(text)
    texts=' '.join(text_list)
    mask = numpy.array(image.open('love.jpg'))
    # stopwords={'nan':0,'em':0,'e113':0,'e112':0,'e114':0,'e120':0}
    word_cloud=WordCloud(
        background_color='black',
        width=500,
        height=500,
        max_words=300,
        max_font_size=50,
        font_path='FZLTXIHK.TTF',
        mask=mask,
        # stopwords=stopwords,
    ).generate(texts)
    WordCloud.to_image(word_cloud).save('说说词云.jpg')


if __name__=='__main__':
    # path=input('请输入文件的路径：').strip()
    data=pd.read_excel('我命由我的说说.xlsx')
    my_cloud(data=data['说说内容'])

