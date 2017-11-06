# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import get_md5

import re
import datetime


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_converter(value):
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def get_nums(value):
    pattern = r'.*?(\d+).*'
    match = re.match(pattern, value)
    if match:
        return int(match.group(1))
    else:
        return 0


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
