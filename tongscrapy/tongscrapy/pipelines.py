# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# import pymysql
# import pymysql.cursors
# import pandas as pd
# from pandas import DataFrame
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import csv

# 数据存储在csv文件里
class savefileTongscrapyPipeline(object):
    def __init__(self):
        self.file = open('py51jobsinfo.csv', 'w', newline='')
        self.csvwriter = csv.writer(self.file)
        self.csvwriter.writerow(['职位名称', '公司名', '地点', '薪资'])
    def process_item(self, item, spider):
        self.csvwriter.writerow([item["position"], item["company"], item["place"], item["salary"]])
        return item
    def close_spider(self, spider):
        self.file.close()

# 数据存储在MySQL数据库里
class mysqlTongscrapyPipeline(object):
    # 采用异步机制写入MySQL
    def __init__(self, dppool):
        self.dppool = dppool

    # 用固定方法 【写法固定】  获取配置文件内信息
    @classmethod
    def from_settings(cls, settings):  # cls实际就是本类 MysqlTwistedPipeline
        dpparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,  # 指定 curosr 类型  需要导入MySQLdb.cursors
            use_unicode=True
        )
        # 由于要传递参数 所以参数名成要与connnect保持一致
        # 用的仍是MySQLdb的库 twisted并不提供
        # 异步操作
        # adbapi # 可以将MySQLdb的一些操作变成异步化操作
        dppool = adbapi.ConnectionPool("MySQLdb", **dpparms)  # 告诉它使用的是哪个数据库模块  连接参数
        # 另外 以上dpparms的参数也可单独写，这样会造成参数列表过大
        return cls(dppool)  # 即实例化一个pipeline

    def process_item(self, item, spider):
        # 使用twisted将mysql插入编程异步操作
        # 指定操作方法和操作的数据 [下面会将方法异步处理]
        query = self.dppool.runInteraction(self.do_insert, item)
        # AttributeError: 'Deferred' object has no attribute 'addErrorback'
        # query.addErrorback(self.handle_error)  # 处理异常
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        # 定义错误 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        """
        此类内其他都可以看作是通用 针对不同的sql操作只需要改写这里即可了
        :param cursor:
        :param item:
        :return:
        """
        insert_sql = """insert into py51jobsinfo(position, company, place, salary)
                                    values (%s, %s, %s, %s)"""

        cursor.execute(insert_sql, (item["position"], item["company"], item["place"], item["salary"]))
        return item
