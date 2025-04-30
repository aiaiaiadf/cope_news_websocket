# 1 服务功能介绍

从kafak拉去数据，然后对数据做分类，然后推给web端，本地做保存。

# 2 本地文档保存格式

```
--news
----爬取的网站名字
------日期
--------新闻标签
----------新闻

```
运行  
python main.py
python server_test.py


运行
uvicorn more_news:app --reload
http://127.0.0.1:8000/docs#/default/post_more_news_more_news_post
# {
#   "date": "2025-04-15_15-51",
#   "max_num": "10",
#   "label": "all"
# }