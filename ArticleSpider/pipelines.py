# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from scrapy.utils.project import get_project_settings

from twisted.enterprise import adbapi

import codecs
import json
import MySQLdb
import MySQLdb.cursors
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            if ok:
                item['front_img_path'] = value['path']
            else:
                item['front_img_path'] = ''

        return item


class JsonWithEncodingPipeline(object):
    # self defined jsonpipeline
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # use the scrapy built-in json writter
    def __init__(self):
        self.file = open('articleJsonExporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class MysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('159.203.72.236', 'root', 'root', 'spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, save_num, url_object_id, content)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["save_num"], item['url_object_id'], item['content']))
        self.conn.commit()


class MysqlTwistedPipeline(object):

        def __init__(self, dbpool):
            self.dbpool = dbpool

        @classmethod
        def from_settings(cls, settings):
            db_param = dict(host=settings['DB_HOST'],
                            port=settings['DB_PORT'],
                            user=settings['DB_USER'],
                            password=settings['DB_PASSWD'],
                            db=settings['DB_DB'],
                            charset='utf8',
                            use_unicode=True,
                            cursorclass=MySQLdb.cursors.DictCursor
                            )
            dbpool = adbapi.ConnectionPool("MySQLdb", **db_param)

            return cls(dbpool)

        def process_item(self, item, spider):
            query = self.dbpool.runInteraction(self._insert_record, item)
            query.addErrback(self._handle_error)
            return item

        def _handle_error(self, e):
            print(e)

        def _insert_record(self, cursor, item):
            insert_sql, values = item.get_insert_sql()

            result = cursor.execute(insert_sql, values)


