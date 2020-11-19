# coding=utf-8
"""
@auth: xiaobei
@date: 2020/11/17 
@desc: 爬虫入口
"""
from scrapy import cmdline


def main():
    cmdline.execute('scrapy crawl snail'.split())


if __name__ == '__main__':
    main()
