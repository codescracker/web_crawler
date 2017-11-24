# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from ArticleSpider.items import LagouJobItem
from ArticleSpider.utils.common import get_md5,date_converter
from ArticleSpider.settings import SQL_DATETIME_FORMAT

import datetime


class LagouSpider(CrawlSpider):
    # header = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    # }

    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']
    proxy = 'http://202.9.104.10:80'

    rules = (

        Rule(LinkExtractor(allow=r'jobs/\d+\.html'), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'zhaopin/*.'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+\.html'), follow=True)
    )

    def _build_request(self, rule, link):
        r = scrapy.Request(url=link.url, callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        # r.meta['proxy'] = self.proxy
        return r

    def start_requests(self):
        for url in self.start_urls:
            r = scrapy.Request(url, dont_filter=True)
            # r.meta['proxy'] = self.proxy
            # yield scrapy.Request(url, dont_filter=True)
            yield r

    def parse_job(self, response):
        job_loader = ItemLoader(item=LagouJobItem(), response=response)

        job_loader.add_value('url', response.url)
        job_loader.add_value('url_object_id', get_md5(response.url))
        job_loader.add_css('title', '.job-name span.name::text')
        job_loader.add_css('salary', '.job_request span.salary::text')
        job_loader.add_xpath('job_city', "//*[@class='job_request']/p/span[2]/text()")
        job_loader.add_xpath('work_experience', "//*[@class='job_request']/p/span[3]/text()")
        job_loader.add_xpath('degree_needed', "//*[@class='job_request']/p/span[4]/text()")
        job_loader.add_xpath('job_type', "//*[@class='job_request']/p/span[5]/text()")
        job_loader.add_css('publish_time', '.publish_time::text')
        job_loader.add_css('tags', '.position-label li.labels::text')
        job_loader.add_css('job_advantage', 'dd.job-advantage p::text')
        job_loader.add_css('job_desc', 'dd.job_bt div')
        job_loader.add_css('job_addr', 'div.work_addr a::text')
        job_loader.add_css('company_url', '#job_company dt a::attr(href)')
        job_loader.add_css('company_name', '#job_company h2.fl::text')
        job_loader.add_value('crawl_time', datetime.datetime.now().strftime(SQL_DATETIME_FORMAT))

        job_item = job_loader.load_item()

        yield job_item

