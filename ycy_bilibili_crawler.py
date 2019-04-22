# -*- coding: utf-8 -*-
from __future__ import print_function
import multiprocessing
import sys
import requests
import os
import time
import io
import json
from you_get import common
directory = r'D:\cut\B站'
dir="ycy_bili"
users={
    "杨超越全国粉丝会":"361372869",
    "杨超越视频站":"107961740"
}
url_search="https://space.bilibili.com/ajax/member/getSubmitVideos?mid={}&pagesize=30&tid=0&page={}&keyword=&order=pubdate"
url_page="https://www.bilibili.com/video/av{}"
def search(user):
    global result
    set_av=set([item["aid"] for item in result])
    uid=users[user]
    page=1
    max=999
    flag=True
    while flag:
        print("{}/{}-{}".format(page,max,user), flush=True)
        try:
            resopnse=requests.get(url_search.format(uid,page))
            data=resopnse.json()
            max=data["data"]["pages"]
            items=data["data"]["vlist"]
            for item in items:
                av=item["aid"]
                if av in set_av:
                    flag = False
                    break
                result.append(item)
            page+=1
            time.sleep(1)
        except Exception as e:
            print(e)
            continue
        dump_json()
        if page > max:
            flag=False
def download_single(av):
    url=url_page.format(av)
    sys.argv = ['you-get','--playlist', '-o', directory, url]
    common.main()
def download():
    set_downloaded=set(downloaded)
    pool = multiprocessing.Pool(processes=32)
    for item in result:
        av=item["aid"]
        if av in set_downloaded:
            continue
        pool.apply_async(download_single, (av,))
    pool.close()
    pool.join()
    print("结束")
def main():
    init()
    # for user in users:
    #     search(user)
    download()
def dump_json():
    def save_as_json(param,filename):
        text = json.dumps(param, ensure_ascii=False, indent=4)
        with io.open(os.path.join(dir, filename), "w", encoding="utf-8") as fd:
            fd.write(text)
    print("正在保存")
    save_as_json(result,"result.json")
    save_as_json(downloaded, "downloaded.json")
    print("保存完毕")
def init():
    global result,crawlered,downloaded,record
    if not os.path.exists(dir):
        os.mkdir(dir)
    if not os.path.exists(os.path.join(dir,"attachments")):
        os.mkdir(os.path.join(dir,"attachments"))
    if not os.path.exists(os.path.join(dir,"backup")):
        os.mkdir(os.path.join(dir,"backup"))
    if os.path.exists(os.path.join(dir,"result.json")):
        result=json.loads(io.open(os.path.join(dir,"result.json"),encoding="utf-8").read())
    else:
        result=[]
    if os.path.exists(os.path.join(dir,"downloaded.json")):
        downloaded=json.loads(io.open(os.path.join(dir,"downloaded.json"),encoding="utf-8").read())
    else:
        downloaded=[]
if __name__=="__main__":
    main()
