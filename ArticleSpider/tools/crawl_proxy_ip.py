import requests
from scrapy.selector import Selector
import MySQLdb
import time
import schedule

mysql_connector = MySQLdb.connect(host='spider.c0kwpumescj5.us-east-1.rds.amazonaws.com',
                                  port=3306, user='root', passwd='Zuoqian690712',
                                  db='spider')

cursor = mysql_connector.cursor()


def crawl_xci_ips():
    headers = {

        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    count = 0
    print("start crawl xici")

    for page in range(0,2000):
        url = 'http://www.xicidaili.com/nn/{0}'.format(page)

        response = requests.get(url, headers=headers)
        selector = Selector(text=response.text)
        tr_list = selector.css('#ip_list tr')
        for tr in tr_list[1:]:
            tds = tr.css('td')
            ip = tds[1].css('::text').extract_first()
            port = tds[2].css('::text').extract_first()
            protocol_type = tds[5].css('::text').extract_first()

            insert_sql = """INSERT INTO proxy_ip(ip, port, protocol_type) VALUES(%s, %s, %s)
                              ON DUPLICATE KEY UPDATE port=VALUES(port)"""

            values = (ip, port, protocol_type)

            try:
                cursor.execute(insert_sql, values)
                mysql_connector.commit()
            except:
                mysql_connector.rollback()

            count+=1

            if count%500==0:
                print('finish', count)

    print("Finish the collecting of proxy ip pool")


def crawl_free_proxy():
    headers = {

        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    url = 'https://free-proxy-list.net/anonymous-proxy.html'

    print("start crawl")
    response = requests.get(url, headers=headers)
    selector = Selector(text=response.text)

    count = 0

    table = selector.css('#proxylisttable')
    tbody = table.css('tbody')
    trs = tbody.css('tr')
    for tr in trs:
        tds = tr.css('td')
        ip = tds[0].css('::text').extract_first()
        port = tds[1].css('::text').extract_first()

        is_https = tds[6].css('::text').extract_first()
        protocol = ''
        if is_https=='yes':
            protocol = 'HTTPS'
        else:
            protocol = 'HTTP'

        insert_sql = """INSERT INTO proxy_ip(ip, port, protocol_type) VALUES(%s, %s, %s)
                          ON DUPLICATE KEY UPDATE port=VALUES(port)"""

        values = (ip, port, protocol)

        try:
            cursor.execute(insert_sql, values)
            mysql_connector.commit()
        except:
            mysql_connector.rollback()

        count+=1

        if count % 50 == 0:
            print('finish', count)

    print("Finish the collecting of proxy ip pool")


class GetIP(object):
    headers = {

        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    def get_random_ip(self):
        random_sql = """SELECT ip,port,protocol_type FROM proxy_ip
                          ORDER BY RAND()
                          LIMIT 1"""

        cursor.execute(random_sql)

        for proxy in cursor.fetchall():
            ip = proxy[0]
            port = proxy[1]
            protocol_type = proxy[2]
            if self.check_proxy(ip, port, protocol_type):
                return '{0}://{1}:{2}'.format('http', ip, port)
            else:
                return self.get_random_ip()

    def check_proxy(self, ip, port, protocol_type):
        test_url = 'https://www.baidu.com/'
        proxy_format = '{0}://{1}:{2}'.format('http', ip, port)
        print(proxy_format)
        if protocol_type=='HTTP':
            proxy_dict = {
                "http": proxy_format
            }
        else:
            proxy_dict = {
                "https": proxy_format
            }

        try:
            response = requests.get(test_url, proxies=proxy_dict, headers = self.headers)
        except:
            print('invalid proxy')
            self.delete_proxy(ip)
            return False
        else:
            code = response.status_code
            if code>=200 and code<=299:
                print('valid proxy')
                return True
            else:
                print('invalid proxy')
                self.delete_proxy(ip)
                return False

    def delete_proxy(self, ip):
        delete_sql = """DELETE From proxy_ip WHERE ip = '{}'""".format(ip)
        print(delete_sql)
        cursor.execute(delete_sql)
        mysql_connector.commit()

if __name__ == '__main__':
    # crawl_xci_ips()
    schedule.every(10).minutes.do(crawl_free_proxy)
    while True:
        schedule.run_pending()
        time.sleep(1)

