#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: LostInNight
# @Date:   2015-10-26 16:02:29
# @Last Modified by:   LostInNight
# @Last Modified time: 2015-10-29 17:38:36


import requests
import configparser
import model
import os
import sys
import time
import re
import json
import threading
from datetime import datetime



class Util(object):
    headers = {
        "Accept-Encoding": "gzip, deflate, sdch",
        # "Host": "www.douban.com", # 获取网页和JSON时的HOST不同，暂取消
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }

    count = 0

    def __init__(self):
        # 将工作目录改为脚本所在的目录，才能直接用文件名读取同目录下其他文件
        os.chdir(sys.path[0])
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.apikey = config['API']['apikey']
        self.lock = threading.Lock()

    # 传入网址或用户id，返回User对象
    # 这里暂时只实现传入用户豆瓣主页
    # 宋乐天的主页 http://www.douban.com/people/songlet/
    def get_user(self, home_url):
        # home_url = r'
        html = self.get_html(home_url)
        user_params_re = re.compile(
        r'<div\s+class="pic">[^>]*?people/(.*?)/">[^>]*?icon/u(\d*?)-[^>]*?alt="(.*?)"')
        data = user_params_re.findall(html)
        uid, id, name = data[0]
        return model.User(id, uid, name)

    # 传入任意相册列表页面，获取所有相册id
    # http://www.douban.com/people/songlet/photos
    def get_all_album_id(self, url):
        html = self.get_html(url)
        num_re = re.compile(r'<span\s+class="count">\(共(\d+)个')
        num = int(num_re.findall(html)[0])
        # 组装相册列表页网址模板
        index = url.find(r"/photos")
        url_pattern = url[0:index] + "/photos?start={0}"
        # 每页显示16条
        pages_num = num / 16 if num % 16 == 0 else int(num / 16) + 1  # 最大页数
        # 也可以下面这么写
        # pages_num = [int(num / 16) + 1, num / 16,][num % 16 == 0]
        urls = [url_pattern.format(x * 16) for x in range(pages_num)]
        album_id_re = re.compile(r'<div\s+class="pl2">[^>]*?album/(\d+)/')
        album_ids = []
        for url in urls:
            html = self.get_html(url)
            album_ids.extend(album_id_re.findall(html))
        return album_ids

    # 获取网页解码后的网页源码
    def get_html(self, url):
        return requests.get(url, headers = self.__class__.headers).text

    # 传入相册id，返回Album对象
    # 相册：https://api.douban.com/v2/album/41583431
    def get_album(self, album_id):
        if self.apikey:
            url_pattern = r'https://api.douban.com/v2/album/{0}?apikey={1}'
            url = url_pattern.format(album_id, self.apikey)
        else:
            url_pattern = r'https://api.douban.com/v2/album/{0}'
            url = url_pattern.format(album_id)
        jsonStr = self.get_html(url)
        data = json.loads(jsonStr)
        title = data['title'].strip()
        url = data['alt']
        author = data['author']['name']
        created = data['created']
        size = int(data['size'])
        desc = data['desc'].strip()
        return model.Album(album_id, title, url, author = author, created = created, size = size, desc = desc)

    # 传入相册id，返回该相册下所有Photo对象
    # 照片列表：https://api.douban.com/v2/album/41583431/photos?start=0&count=100
    def get_photos(self, album_id):
        if self.apikey:
            url_pattern = r'https://api.douban.com/v2/album/{0}/photos?start={1}&count=100&apikey={2}'
            url = url_pattern.format(album_id, 0, self.apikey)
        else:
            url_pattern = r'https://api.douban.com/v2/album/{0}/photos?start={1}&count=100'
            url = url_pattern.format(album_id, 0)
        jsonStr = self.get_html(url)
        data = json.loads(jsonStr)
        size = int(data['album']['size'])
        # 分N次提取。每次最多100条
        part = size / 100 if size % 100 == 0 else int(size/100) + 1
        urls = [url.format(album_id, x*100, self.apikey) for x in range(part)]
        photos = []
        for url in urls:
            jsonStr = self.get_html(url)
            data = json.loads(jsonStr)
            for x in data['photos']:
                id = x['id']
                # 有的相册里没有large，那就取image
                if 'large' in x.keys():
                    url = x['large']
                elif 'image' in x.keys():
                    url = x['image']
                elif 'cover' in x.keys():
                    url = x['cover']
                position = x['position']
                desc = x['desc'].strip().strip()
                created = x['created']
                liked_count = x['liked_count']
                comments_count = x['comments_count']
                album_title = x['album_title'].strip()
                album_id = x['album_id']
                author_name = x['author']['name']
                author_id = x['author']['id']
                author_uid = x['author']['uid']
                photo = model.Photo(id, url,
                    position=position, desc= desc, created=created,
                    liked_count=liked_count, comments_count=comments_count,
                    album_title=album_title, album_id = album_id,
                    author_name=author_name, author_id=author_id,
                    author_uid=author_uid)
                photos.append(photo)
        return photos

    # 传入照片id，返回单个Photo对象
    # 照片：https://api.douban.com/v2/photo/2098250723
    def get_photo(self, photo_id):
        if self.apikey:
            url_pattern = r'https://api.douban.com/v2/photo/{0}?apikey={1}'
            url = url_pattern.format(photo_id, self.apikey)
        else:
            url_pattern = r'https://api.douban.com/v2/photo/{0}'
            url = url_pattern.format(photo_id)
        jsonStr = self.get_html(url)
        data = json.loads(jsonStr)
        url = data['large']
        position = data['position']
        desc = data['desc']
        created = data['created']
        liked_count = data['liked_count']
        comments_count = data['comments_count']
        album_title = data['album_title']
        album_id = data['album_id']
        author_name = data['author']['name']
        author_id = data['author']['id']
        author_uid = data['author']['uid']
        return model.Photo(id, url,
                    position=position, desc= desc, created=created,
                    liked_count=liked_count, comments_count=comments_count,
                    album_title=album_title, album_id = album_id,
                    author_name=author_name, author_id=author_id,
                    author_uid=author_uid)

    # 保存照片，如果是单个文件也要构造成单元素列表传进来
    def save(self, photos, path):
        # 以相册名为文件夹保存
        filepath = os.path.join(path, photos[0].album_title)
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        for photo in photos:
            self.lock.acquire()
            try:
                self.print_info(photo)
            except Exception as e:
                raise e
                continue
            finally:
                self.lock.release()
            # 避免传进来的position是个数字
            filename = '{0}{1}'.format(photo.position, os.path.splitext(photo.url)[1])
            file = os.path.join(filepath, filename)
            response = requests.get(photo.url, headers=self.__class__.headers)
            with open(file, 'wb') as f:
                f.write(response.content)

    # 判断传入的是网址类型，返回需要进行的操作
    # 用户主页：http://www.douban.com/people/songlet/
    # 相册列表：http://www.douban.com/people/songlet/photos
    # 相册列表2：http://www.douban.com/people/songlet/photos?start=32
    # 照片列表：http://www.douban.com/photos/album/65355331/
    # 照片列表2：http://www.douban.com/photos/album/65355331/?start=90
    # 照片页：http://www.douban.com/photos/photo/1515461400/
    def judge_url(self, url):
        re_user = re.compile(r'^http://www.douban.com/people/[^/]+?/?$')
        re_album_list = re.compile(r'^http://www.douban.com/people/[^/]+?/photos[^/]*?$')
        re_photo_list = re.compile(r'^http://www.douban.com/photos/album/\d+/?[^/]*?$')
        re_photo = re.compile(r'^http://www.douban.com/photos/photo/\d+/?$')
        # 如果没有HTTP头就加上
        if not url.startswith('http://'):
            url = 'http://' + url
        if re_user.match(url):
            return 'user'
        if re_album_list.match(url):
            return 'album_list'
        if re_photo_list.match(url):
            return 'photo_list'
        if re_photo.match(url):
            return 'photo'
        return None



    # 打印当前下载信息
    def print_info(self, photo):
        self.__class__.count += 1
        print('正在下载相册 %s 第 %s 张照片。总下载数： %s' %(photo.album_title, photo.position, self.__class__.count))
        # 控制台是GBK编码，遇到无法显示的UTF-8字符时会报错。所以取消了照片信息的输出
        # print('照片信息：', photo.desc)
        print('照片网址：', photo.url)
        print('当前时间：', datetime.now())
        print('当前线程数：', threading.active_count())
        print('-'*40)

    # 下载
    def down(self, album_id, savepath):
        # 下载
        photos = self.get_photos(album_id)
        self.save(photos, savepath)

    # 主方法
    def main(self, url, savepath):
        judge = self.judge_url(url)
        if judge == None:
            print('网址错误！请检查输入！')
            exit(0)
        # 传入用户主页或相册列表页，则下载所有
        if judge.lower() == 'user':
            user = self.get_user(url)
            uid = user.uid
            # 相册列表页网址
            url = r'http://www.douban.com/people/{0}/photos'.format(uid)
            album_ids = self.get_all_album_id(url)
        elif judge.lower() == 'album_list':
            album_ids = self.get_all_album_id(url)
        # 下载所有照片
        elif judge.lower() == 'photo_list':
            re_album_id = re.compile(r'album/(\d+)/')
            album_id = re_album_id.findall(url)[0]
            album_ids = [album_id]
        elif judge.lower() == 'photo':
            jsonStr = self.get_html(url)
            data = json.loads(jsonStr)
            album_id = data['album_id']
            album_ids = [album_id]

        t = []
        # 多线程下载
        for album_id in album_ids:
            t.append(threading.Thread(target=self.down, args = (album_id, savepath)))

        for x in t:
            x.daemon = True
            x.start()
        # 如果join写在上一个循环里，主线程会停止循环并等待子线程结束
        for x in t:
            x.join()

        print('下载完成！')




# 秒-->时分秒
def trans_time(sec):
    hour = int(sec / 3600)
    sec = sec % 3600
    minute = int(sec / 60)
    sec = sec % 60
    return "%s小时 %s分 %s秒" % (hour, minute, sec)


if __name__ == '__main__':
    print('使用说明：')
    print('豆瓣个人主页网址--->下载该用户所有相册')
    print('豆瓣相册列表网址--->下载该用户所有相册')
    print('豆瓣照片列表网址--->下载该相册所有照片')
    print('豆瓣照片网址--->载该相册所有照片')
    print('='*20)
    url = input('请输入：')
    path = input('请输入保存结果用的文件夹:')

    # url = r'http://www.douban.com/people/songlet/photos'
    # path = r'F:\宋乐天相册'


    start = time.time()
    Util().main(url, path)
    used_time = trans_time(time.time() - start)
    print('抓取完成！\n耗时 %s\n请查看 %s' % (used_time, path))
