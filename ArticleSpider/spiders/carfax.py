# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
import json
from ArticleSpider.items import CarFaxItem
from ArticleSpider.settings import SQL_DATETIME_FORMAT
import datetime


class CarfaxSpider(scrapy.Spider):
    name = 'carfax'
    allowed_domains = ['carfax.com']
    start_urls = ['https://www.carfax.com/cars-for-sale/']

    def start_requests(self):
        browser = webdriver.Chrome()
        make_urls = []

        for start_url in self.start_urls:
            browser.get(start_url)
            options = browser.find_elements_by_css_selector('select[name=make] optgroup option')
            for opt in options:
                make = opt.get_attribute('value')
                if len(make.split())>1:
                    make = '+'.join(make.split())

                url_base = 'https://www.carfax.com/api/vehicles'
                url = url_base+'?'+'make='+make
                make_urls.append((make, url))

        browser.close()

        for make_url in make_urls:
            make, url = make_url
            yield scrapy.Request(url=url, callback=self.parse, meta={'car_make': make})

    def parse(self, response):
        car_make = response.meta.get('car_make')

        data = json.loads(response.text)
        current_page = data['page']
        total_page = data['totalPageCount']

        info_list = data['listings']
        for info in info_list:
            car_item = CarFaxItem()

            car_item['dealer_id'] = info['dealer']['carfaxId']
            car_item['dealer_name'] = info['dealer']['name']
            car_item['dealer_city'] = info['dealer']['city']
            car_item['dealer_state'] = info['dealer']['state']

            car_item['car_vin'] = info['vin']
            car_item['car_year'] = info['year']
            car_item['car_make'] = info['make']
            car_item['car_topOptions'] = ','.join(info['topOptions']) if info['topOptions'] else ''
            car_item['car_model'] = info['model']
            car_item['car_trim'] = info['trim']
            car_item['car_mileage'] = info['mileage']
            car_item['car_list_price'] = info['listPrice']
            car_item['car_current_price'] = info['currentPrice']
            car_item['car_exteriorColor'] = info['exteriorColor']
            car_item['car_interiorColor'] = info['interiorColor']
            car_item['car_engine'] = info['engine']
            car_item['car_displacement'] = info['displacement']
            car_item['car_drivetype'] = info['drivetype']
            car_item['car_transmission'] = info['transmission']
            car_item['car_fuel'] = info['fuel']
            car_item['car_mpgCity'] = info['mpgCity']
            car_item['car_mpgHighway'] = info['mpgHighway']
            car_item['car_mpgCombined'] = info['mpgCombined']
            car_item['car_bodytype'] = info['bodytype']
            car_item['car_oneOwner'] = info['oneOwner']
            car_item['car_noAccidents'] = info['noAccidents']
            car_item['car_serviceRecords'] = info['serviceRecords']
            car_item['car_personalUse'] = info['personalUse']

            car_item['crawl_time'] = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

            yield car_item

        if current_page<total_page:
            next_page = current_page+1
            next_url = 'https://www.carfax.com/api/vehicles?make={0}&page={1}'.format(car_make, next_page)
            yield scrapy.Request(next_url, callback=self.parse, meta={'car_make': car_make})

