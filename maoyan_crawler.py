# -*- coding: utf-8 -*-
import io
import os
import memcache
import json
import zlib
import random
import grequests
import time
from fake_useragent import UserAgent
ua=UserAgent()
client = memcache.Client(['127.0.0.1:11211'])
proxys = [line.replace("\n", "") for line in open("/home/maoyan/maoyan/proxy.txt", "r").readlines()]
url_page="http://m.maoyan.com/sns/assist/assemble/detail.json?assembleId={}"
tasks_per_cycle=1024
timeout_global=10
fail_ignore_threshold=10
def crawler(start,end):
    global done,data,fail,other,todo
    def exception_handler(request, exception):
        global fail
        fail += 1
        return
    if start>end:
        start,end=end,start
    data=client.get("data")
    if data:
        data=zlib.decompress(data)
        data=json.loads(data)
    else:
        data={}
    for key in range(start,end):
        if not str(key) in data:
            data[str(key)]={"n":1,"t":3600}
    done=client.get("done")
    if done:
        done=zlib.decompress(done)
        done=list(set(json.loads(done)))
    else:
        done=[]
    other=client.get("other")
    if other:
        other=zlib.decompress(other)
        other=list(set(json.loads(other)))
    else:
        other=[]
    set_done=set(done)
    set_other=set(other)
    set_todo=set(todo)
    total = []
    for key in data:
        item = data[key]
        number = item["n"]
        time_remain = item["t"]
        if time_remain > 60 and number < 5 and int(key)<end:
            if key in set_done or key in set_other or key in set_todo:
                continue
            total.append(key)
    fail=0
    indeies = {}
    tasks = []
    count=0
    times=len(total)/tasks_per_cycle
    if times==0:
        times=1
    for i in range(times):
        start=i*tasks_per_cycle
        end=(i+1)*tasks_per_cycle
        if end>len(total):
            groups = total[start:]
        else:
            groups=total[start:end]
        for id in groups:
            headers = {
                "User-Agent": ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Host": "m.maoyan.com",
                "Upgrade-Insecure-Requests": "1"
            }
            proxy = random.choice(proxys)
            task = grequests.get(url_page.format(id), headers=headers, proxies={"https": proxy, "http": proxy},
                                 timeout=timeout_global)
            tasks.append(task)
            indeies[count]=id
            count +=1
        if len(tasks)>=tasks_per_cycle or end>len(total):
            time_start = time.time()
            responses = grequests.map(tasks, exception_handler=exception_handler)
            time_end = time.time()
            print("共计{}个请求,耗时:{}秒".format(len(total),int(time_end-time_start)))
            count=0
            for j in range(len(tasks)):
                response=responses[j]
                if response==None:
                    continue
                if response.status_code!=200:
                    fail += 1
                    continue
                id=indeies[j]
                try:
                    response = response.json()
                except:
                    continue
                if "error" in response:
                    if response["error"]["code"]==10404:
                        todo.append(id)
                        count += 1
                    else:
                        print("{}-{}".format(id,response["message"]))
                        fail += 1
                    continue
                if response["data"]["celebrityId"]!=2854373:
                    if id in data:
                        del data[id]
                    other.append(id)
                    continue
                number=len(response["data"]["users"])
                if number>4:
                    done.append(id)
                time_remain=response["data"]["expireSeconds"]
                if time_remain==0:
                    done.append(id)
                todo.append(id)
                count += 1
                if data[id]["t"]>time_remain:
                    data[id]={"n":number,"t":time_remain}
            print("共计成功请求{}次,失败{}次,共计{}次".format(count,fail,len(tasks)))
            count = 0
            indeies = {}
            tasks = []
            done_str=zlib.compress(json.dumps(done))
            client.set("done",done_str)
            data_str=zlib.compress(json.dumps(data))
            client.set("data",data_str)
            other_str=zlib.compress(json.dumps(other))
            client.set("other",other_str)
            # dump_json()
            if end<len(total):
                return 1
            if fail<=fail_ignore_threshold:
                return 0
def dump_json():
    global done,data,other
    def save_as_json(param,filename):
        text = json.dumps(param, ensure_ascii=False, indent=4)
        if type(text) == str:
            text = text.decode("utf-8")
        with io.open("/home/maoyan/"+filename, "w", encoding="utf-8") as fd:
            fd.write(text)
    print("正在保存")
    save_as_json(done,"done.json")
    save_as_json(data,"data.json")
    save_as_json(other, "other.json")
    print("保存完毕")
def main():
    global todo,fail_ignore_threshold
    todo=[]
    start=client.get("start")
    end=client.get("end")
    print("{}-{}".format(start, end))
    fail_ignore_threshold=10
    while True:
        result=crawler(start,end)
        if result==0:
            break
if __name__=="__main__":
    main()
