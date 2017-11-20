# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader

from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem

import re
import json
import os
from urllib import parse
import datetime


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    header = {
        'Host': 'www.zhihu.com',
        "Referer": "https://www.zhizhu.com",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    def start_requests(self):
        url = 'https://www.zhihu.com/#signin'

        return [scrapy.Request(url, callback=self.log_in, headers=self.header)]

    def log_in(self, response):
        # here you would extract links to follow and return Requests for
        # each of them, with another callback
        response_text = response.text
        csrf_pattern = r'.*name="_xsrf" value="(.*)"'
        csrf_match = re.match(csrf_pattern, response_text, re.S)
        csrf = ''
        if csrf_match:
            csrf = csrf_match.group(1)

        if csrf:

            post_data = dict()
            post_data['phone_num'] = '5083088487'
            post_data['password'] = 'Zuoqian690712'
            post_data['_xsrf'] = csrf
            post_data['captcha'] = ''

            import time
            t = str(int(time.time() * 1000))
            captcha_url = 'https://www.zhihu.com/captcha.gif?r={}&type=login'.format(t)
            return [scrapy.Request(captcha_url, callback=self.log_after_captcha, headers=self.header,
                                   meta={'post_data': post_data})]

    def log_after_captcha(self, response):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'async_captcha.jpg'), 'wb') as f:
            f.write(response.body)

        from PIL import Image
        try:
            im = Image.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'async_captcha.jpg'))
            im.show()
            im.close()
        except:
            pass

        captcha = input("input the captcha \n >")

        post_url = 'https://www.zhihu.com/login/phone_num'

        post_data = response.meta.get('post_data')
        post_data['captcha'] = captcha

        return [scrapy.FormRequest(post_url,
                                   formdata=post_data,
                                   callback=self.check_login,
                                   headers=self.header)]

    def check_login(self, response):
        response_data = json.loads(response.text)
        if 'msg' in response_data and response_data['msg'] == "登录成功":
            print(response_data['msg'])
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers= self.header, callback= self.parse)
        else:
            print(response_data['msg'])

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)

        url_pattern = r'(https://www.zhihu.com/question/(\d+))($|/)*.'

        for url in all_urls:
            re_match = re.match(url_pattern, url)
            if re_match:
                question_url = re_match.group(1)
                question_id = re_match.group(2)

                yield scrapy.Request(url=question_url, headers= self.header, callback=self.parse_question, meta={'question_id': question_id})

            else:
                yield scrapy.Request(url=url, headers= self.header, callback=self.parse)

    def parse_question(self, response):

        question_id = int(response.meta.get('question_id'))
        # handle new version
        if "QuestionHeader-title" in response.text:
            print("This is the new version of Zhihu")

            question_loader = ItemLoader(item= ZhihuQuestionItem(), response= response)

            question_loader.add_value('url', response.url)
            question_loader.add_value('zhihu_id', question_id)
            question_loader.add_css('title', "h1.QuestionHeader-title::text")
            question_loader.add_css('content', "div.QuestionHeader-detail")
            question_loader.add_css('answer_num', "h4.List-headerText span::text")
            question_loader.add_css('comments_num', "div.QuestionHeader-Comment button::text")
            question_loader.add_css('watch_user_num', "div.NumberBoard-value::text")
            question_loader.add_css('topics', "div.QuestionHeader-topics .Popover div::text")

        else:
            print("This is the old version of Zhihu")
            question_loader = ItemLoader(item= ZhihuQuestionItem(), response= response)

            question_loader.add_value('url', response.url)

            question_loader.add_value('zhihu_id', question_id)
            question_loader.add_xpath("title",
                                      "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            question_loader.add_css("content", "#zh-question-detail")
            question_loader.add_css("answer_num", "#zh-question-answer-num::text")
            question_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            question_loader.add_xpath("watch_user_num",
                                      "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            question_loader.add_css("topics", ".zm-tag-editor-labels a::text")

        question_item = question_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers= self.header, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        response_text = response.text
        response_json = json.loads(response_text)

        is_end = response_json['paging']['is_end']

        for answer in response_json['data']:
            answser_item = ZhihuAnswerItem()

            answser_item['zhihu_id'] = answer['id']
            answser_item['url'] = answer['url']
            answser_item['question_id'] = answer['question']['id']
            answser_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answser_item['content'] = answer['content'] if 'content' in answer else None
            answser_item['praise_num'] = answer['voteup_count']
            answser_item['comments_num'] = answer['comment_count']
            answser_item['create_time'] = answer['created_time']
            answser_item['update_time'] = answer['updated_time']
            answser_item['crawl_time'] = datetime.datetime.now()
            yield answser_item

        if not is_end:
            next_answer_url = response_json['paging']['next']
            yield scrapy.Request(next_answer_url, headers=self.header, callback=self.parse_answer)



