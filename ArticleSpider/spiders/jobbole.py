# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader

from urllib import parse

from ArticleSpider.items import JobboleArticleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_nodes = response.css(" div[id='archive'] .floated-thumb .post-thumb a ")
        for post_node in post_nodes:
            img_url = post_node.css("img::attr(src)").extract_first('')
            post_url = post_node.css("::attr(href)").extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={'front_img_url': parse.urljoin(response.url, img_url)},
                          callback=self.parse_detail)

        next_page_url = response.xpath(
            "//div[contains(@class, 'navigation')]//a[contains(@class,'next' )]/@href").extract_first()
        if next_page_url:
            yield Request(url=parse.urljoin(response.url, next_page_url), callback=self.parse)

    def parse_detail(self, response):
        # article_item = JobboleArticleItem()
        #
        # front_img_url = response.meta.get('front_img_url', '')
        # print(front_img_url)
        #
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        #
        # create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace('·', '').strip()
        # try:
        #     create_date = datetime.datetime.strptime(create_date, '%Y/%m/%d').date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        #
        # thumb_up = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        # if thumb_up:
        #     thumb_up = int(thumb_up)
        # else:
        #     thumb_up = 0
        #
        # save_num = 0
        # save_text = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        # save_pattern = r'(.*)收藏'
        # save_match = re.match(save_pattern,save_text)
        # if save_match:
        #     save_target = save_match.group(1).strip()
        #     if save_target:
        #         save_num = int(save_target)
        #
        # comment_num = 0
        # comment_text = response.xpath("//a[@href = '#article-comment']/span/text()").extract()[0]
        # comment_pattern = r'(.*)评论'
        # comment_match = re.match(comment_pattern, comment_text)
        # if comment_match:
        #     comment_target = comment_match.group(1).strip()
        #     if comment_target:
        #         comment_num = int(comment_target)
        #
        # content = response.xpath("//div[@class = 'entry']").extract()[0]
        #
        # tag_raw = response.css(".entry-meta-hide-on-mobile > a ::text").extract()
        # tag = ','.join([element for element in tag_raw if '评论' not in element])
        #
        # article_item['url'] = response.url
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['title'] = title
        # article_item['create_date'] = create_date
        # article_item['thumb_up'] = thumb_up
        # article_item['save_num'] = save_num
        # article_item['comment_num'] = comment_num
        # article_item['content'] = content
        # article_item['tag'] = tag
        # article_item['front_img_url'] = [front_img_url]

        item_loader = ItemLoader(item=JobboleArticleItem(), response=response)

        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', response.url)
        item_loader.add_value('front_img_url', response.meta.get('front_img_url', ''))

        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_xpath('create_date', "//p[@class='entry-meta-hide-on-mobile']/text()")
        item_loader.add_xpath('thumb_up', "//span[contains(@class, 'vote-post-up')]/h10/text()")
        item_loader.add_xpath('save_num', "//span[contains(@class, 'bookmark-btn')]/text()")
        item_loader.add_xpath('comment_num', "//a[@href = '#article-comment']/span/text()")
        item_loader.add_xpath('content', "//div[@class = 'entry']")
        item_loader.add_css('tag', ".entry-meta-hide-on-mobile > a ::text")

        article_item = item_loader.load_item()

        yield article_item
