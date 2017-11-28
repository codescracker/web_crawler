# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import get_md5, get_nums, date_converter
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

import re
import datetime
from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def tag_filter(value):
    if '评论' not in value:
        return value
    else:
        return ''


class JobboleArticleItem(scrapy.Item):
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    url_object_id = scrapy.Field(
        input_processor=MapCompose(get_md5),
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        output_processor=TakeFirst()
    )

    create_date = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip().replace('·', '').strip(), date_converter),
        output_processor=TakeFirst()
    )
    thumb_up = scrapy.Field(
        input_processor=MapCompose(get_nums),
        output_processor=TakeFirst()
    )
    save_num = scrapy.Field(
        input_processor=MapCompose(get_nums),
        output_processor=TakeFirst()
    )
    comment_num = scrapy.Field(
        input_processor=MapCompose(get_nums),
        output_processor=TakeFirst()
    )
    content = scrapy.Field(
        output_processor=TakeFirst()
    )
    tag = scrapy.Field(
        input_processor=MapCompose(tag_filter),
        output_processor=Join(',')
    )

    front_img_url = scrapy.Field()
    front_img_path = scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """ INSERT INTO jobbole_article(title, url, create_date, url_object_id, front_image_url,
                front_image_path, thumb_up, save_num, comment_num, content, tag )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE save_num=VALUES(save_num), comment_num = VALUES(comment_num)"""

        values = (self['title'], self['url'], self['create_date'], self['url_object_id'], self['front_img_url'][0],
                  self['front_img_path'], self['thumb_up'], self['save_num'], self['comment_num'], self['content'],
                  self['tag'])

        return insert_sql, values


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):

        # need to process the raw data before get into the pipeline
        zhihu_id = self['zhihu_id'][0]
        topics = ','.join(self['topics'])
        url = self['url'][0]
        title = self['title'][0]
        content = self['content'][0]
        answer_num = get_nums(''.join(self['answer_num']))
        comments_num = get_nums(''.join(self['comments_num']))
        if len(self['watch_user_num'][0])==2:
            watch_user_num = int(self['watch_user_num'][0])
            click_num = int(self['watch_user_num'][1])
        else:
            watch_user_num = int(self['watch_user_num'][0])
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        insert_sql = """ INSERT INTO zhihu_question(zhihu_id, topics, url, title, content,
                answer_num, comments_num, watch_user_num, click_num,crawl_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
                watch_user_num = VALUES(watch_user_num), click_num = VALUES(click_num), crawl_time =VALUES(crawl_time)"""

        values = (zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)

        return insert_sql, values


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id= scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """ INSERT INTO zhihu_answer(zhihu_id, url, question_id, author_id,
                content, praise_num, comments_num, create_time, update_time, crawl_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE praise_num=VALUES(praise_num), comments_num=VALUES(comments_num)"""

        values = (self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'],
                  self['praise_num'], self['comments_num'],
                  datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT),
                  datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT),
                  self['crawl_time'].strftime(SQL_DATETIME_FORMAT))

        return insert_sql, values


class LagouJobItem(scrapy.Item):
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    url_object_id = scrapy.Field(
        output_processor=TakeFirst()
    )
    title= scrapy.Field(
        output_processor=TakeFirst()
    )
    salary= scrapy.Field(
        output_processor=TakeFirst()
    )
    job_city= scrapy.Field(
        input_processor=MapCompose(lambda x : x.replace('/','').strip()),
        output_processor=TakeFirst()
    )
    work_experience= scrapy.Field(
        input_processor=MapCompose(lambda x: x.replace('/', '').strip()),
        output_processor=TakeFirst()
    )
    degree_needed= scrapy.Field(
        input_processor=MapCompose(lambda x: x.replace('/', '').strip()),
        output_processor=TakeFirst()
    )
    job_type= scrapy.Field(
        output_processor=TakeFirst()
    )
    publish_time= scrapy.Field(
        output_processor=TakeFirst()
    )
    tags= scrapy.Field(
        output_processor=Join(',')
    )
    job_advantage= scrapy.Field(
        output_processor=TakeFirst()
    )
    job_desc= scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip(), remove_tags, lambda x : x.strip()),
        output_processor=TakeFirst()
    )
    job_addr= scrapy.Field(
        input_processor=MapCompose(lambda x: x if x!= u'查看地图' else ''),
        output_processor=Join('-')
    )
    company_url= scrapy.Field(
        output_processor=TakeFirst()
    )
    company_name= scrapy.Field(
        input_processor=MapCompose(lambda x: x.replace('/', '').strip()),
        output_processor=Join('')
    )
    crawl_time= scrapy.Field(
        output_processor=TakeFirst()
    )
    crawl_update_time= scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """ INSERT INTO lagou(url, url_object_id, title,
                salary, job_city, work_experience, degree_needed, job_type, publish_time,
                tags, job_advantage, job_desc, job_addr, company_url, company_name, crawl_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE salary=VALUES(salary)"""

        values = (self['url'], self['url_object_id'], self['title'], self['salary'], self['job_city'], self['publish_time'],
                  self['work_experience'], self['degree_needed'], self['job_type'], self['publish_time'],
                  self['job_advantage'], self['job_desc'], self['job_addr'].rstrip('-'), self['company_url'], self['company_name'],
                  self['crawl_time'])

        return insert_sql, values


class CarFaxItem(scrapy.Item):
    dealer_id = scrapy.Field()
    dealer_name = scrapy.Field()
    dealer_city =scrapy.Field()
    dealer_state =scrapy.Field()

    car_vin =scrapy.Field()
    car_year =scrapy.Field()
    car_make =scrapy.Field()
    car_topOptions =scrapy.Field()
    car_model =scrapy.Field()
    car_trim =scrapy.Field()
    car_mileage =scrapy.Field()
    car_list_price =scrapy.Field()
    car_current_price =scrapy.Field()
    car_exteriorColor =scrapy.Field()
    car_interiorColor =scrapy.Field()
    car_engine =scrapy.Field()
    car_displacement =scrapy.Field()
    car_drivetype =scrapy.Field()
    car_transmission =scrapy.Field()
    car_fuel =scrapy.Field()
    car_mpgCity =scrapy.Field()
    car_mpgHighway =scrapy.Field()
    car_mpgCombined =scrapy.Field()
    car_bodytype =scrapy.Field()
    car_oneOwner =scrapy.Field()
    car_noAccidents =scrapy.Field()
    car_serviceRecords =scrapy.Field()
    car_personalUse =scrapy.Field()

    crawl_time =scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """ INSERT INTO carfax(dealer_id, dealer_name, dealer_city, dealer_state,
                car_vin, car_year, car_make, car_topOptions, car_model, car_trim, car_mileage,
                car_list_price, car_current_price, car_exteriorColor, car_interiorColor, car_engine,
                car_displacement, car_drivetype, car_transmission, car_fuel, car_mpgCity, car_mpgHighway,
                car_mpgCombined, car_bodytype, car_oneOwner, car_noAccidents, car_serviceRecords, car_personalUse,
                crawl_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE car_current_price=VALUES(car_current_price)"""

        values = (self['dealer_id'], self['dealer_name'], self['dealer_city'], self['dealer_state'],
                  self['car_vin'], self['car_year'], self['car_make'], self['car_topOptions'], self['car_model'],
                  self['car_trim'], self['car_mileage'], self['car_list_price'], self['car_current_price'],
                  self['car_exteriorColor'], self['car_interiorColor'], self['car_engine'], self['car_displacement'],
                  self['car_drivetype'], self['car_transmission'], self['car_fuel'], self['car_mpgCity'], self['car_mpgHighway'],
                  self['car_mpgCombined'], self['car_bodytype'], self['car_oneOwner'], self['car_noAccidents'],
                  self['car_serviceRecords'], self['car_personalUse'], self['crawl_time'])

        return insert_sql, values







