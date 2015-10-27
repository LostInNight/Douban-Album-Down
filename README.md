批量下载豆瓣相册。


## 说明
- Douban.sublime-workspace是Sublime Text 3 的workspac文件。与爬虫本身无关
- 豆瓣API请自行申请，然后写入同目录下的config.ini，格式如下：
```
[API]
apikey = xxxxxxxxxxxx
```


## Change log
2015.10.27：刚完成单线程爬虫，已经可以使用。程序入口是util.py

## TODO
- 改成多线程。控制每秒钟爬网页的次数
- 添加选择相册再下载的功能
- 用数据库或者Excel、CSV等保存抓取过程中的数据，用于意外崩溃后继续
- 添加logging模块，导出日志文件
- 添加GUI界面

暂时只想到这么些，慢慢加。


## Author
Email:jwgmail@126.com
Blog : [http://blog.csdn.net/kinglearnjava](http://blog.csdn.net/kinglearnjava)
