# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
import os
import io
import json
from wordcloud import WordCloud
import jieba
dir="weibo_comment"
def main():
    if not os.path.exists("images"):
        os.mkdir("images")
    data=json.loads(io.open(os.path.join(dir, "result.json"), encoding="utf-8").read())
    delta=datetime.timedelta(days=30)
    date_start=datetime.datetime.strptime("2017-08-04 13:32:43", '%Y-%m-%d %H:%M:%S')
    text=''
    for item in data:
        date=datetime.datetime.strptime(item["date"], '%Y-%m-%d %H:%M:%S')
        text += item['text']+"\n"
        if date+delta>date_start:
            cut_text = " ".join(jieba.cut(text))
            wordcloud = WordCloud(font_path="C:/Windows/Fonts/simfang.ttf",background_color="white",width=1920,height=1080).generate(cut_text)
            filename=date_start.strftime("%Y-%m-%d")
            print(filename)
            wordcloud.to_file('images/{}.png'.format(filename))
            date_start+=delta
            text=''
if __name__=="__main__":
    main()