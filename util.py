#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: LostInNight
# @Date:   2015-10-26 16:02:29
# @Last Modified by:   LostInNight
# @Last Modified time: 2015-10-26 21:57:50


#------------------输入豆瓣相册列表网址，下载所有相册照片-----------------

import requests
import configparser
import model
import os
import sys
import time
import re
import json

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
        url_pattern = r'https://api.douban.com/v2/album/{0}?apikey={1}'
        url = url_pattern.format(album_id, self.apikey)
        jsonStr = self.get_html(url)
        data = json.loads(jsonStr)
        title = data['title']
        url = data['alt']
        author = data['author']['name']
        created = data['created']
        size = int(data['size'])
        desc = data['desc']
        return model.Album(album_id, title, url, author = author, created = created, size = size, desc = desc)

    # 传入相册id，返回该相册下所有Photo对象
    # 照片列表：https://api.douban.com/v2/album/41583431/photos?start=0&count=100
    def get_photos(self, album_id):
        url_pattern = r'https://api.douban.com/v2/album/{0}/photos?start={1}&count=100&apikey={2}'
        url = url_pattern.format(album_id, 0, self.apikey)
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
                url = x['large']
                position = x['position']
                desc = x['desc']
                created = x['created']
                liked_count = x['liked_count']
                comments_count = x['comments_count']
                album_title = x['album_title']
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
        url_pattern = r'https://api.douban.com/v2/photo/{0}?apikey={1}'
        url = url_pattern.format(photo_id, self.apikey)
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
            self.print_info(photo)
            # 避免传进来的position是个数字
            filename = '{0}{1}'.format(photo.position, os.path.splitext(photo.url)[1])
            file = os.path.join(filepath, filename)
            response = requests.get(photo.url, headers=self.__class__.headers)
            with open(file, 'wb') as f:
                f.write(response.content)

    # 打印当前下载信息
    def print_info(self, photo):
        self.__class__.count += 1
        print('正在下载相册 %s 第 %s 张照片。总下载数： %s' %(photo.album_title, photo.position, self.__class__.count))
        print('照片信息：', photo.desc)
        print('照片网址：', photo.url)
        print('-'*40)

    # 主方法
    def main(self, url, path):
        album_ids = self.get_all_album_id(url)
        for album_id in album_ids:
            photos = self.get_photos(album_id)
            self.save(photos, path)



# 秒-->时分秒
def trans_time(sec):
    hour = int(sec / 3600)
    sec = sec % 3600
    minute = int(sec / 60)
    sec = sec % 60
    return "%s小时 %s分 %s秒" % (hour, minute, sec)


if __name__ == '__main__':
    url = input('请输入豆瓣相册列表的完整网址：')
    path = input('请输入保存结果用的文件夹:')

    # url = r'http://www.douban.com/people/songlet/photos'
    # path = r'F:\宋乐天相册'


    start = time.time()
    util = Util()
    util.main(url, path)
    used_time = trans_time(time.time() - start)
    print('抓取完成！\n耗时 %s\n请查看 %s' % (used_time, path))
