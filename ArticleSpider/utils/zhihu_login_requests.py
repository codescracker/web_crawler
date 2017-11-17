import requests
import os

import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')

try:
    session.cookies.load(ignore_discard = True)
    print('Load Cookie')
except:
    print("Cannot load Cookie")


agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
header = {
    'Host': 'www.zhihu.com',
    "Referer": "https://www.zhizhu.com",
    'User-Agent': agent
}


def is_login():
    inbox_url = 'https://www.zhihu.com/inbox'
    response = session.get(inbox_url, headers = header, allow_redirects = False)
    if response.status_code==200:
        return True
    else:
        return False


def get_captcha():
    import time
    t = str(int(time.time()*1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r={}&type=login'.format(t)
    response = session.get(captcha_url, headers = header)
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'captcha.jpg'), 'wb') as f:
        f.write(response.content)

    from PIL import Image
    try:
        im = Image.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'captcha.jpg'))
        im.show()
        im.close()
    except:
        pass

    captcha = input("input the captcha \n >")
    return captcha


def get_index():
    url = 'https://www.zhihu.com'
    response = session.get(url, headers = header)
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'index_page.html'), 'wb') as f:
        f.write(response.text.encode('utf-8'))
    print('OK')


def get_csrf():
    response = session.get('https://www.zhihu.com', headers = header)
    text = response.text

    pattern = r'.*name="_xsrf" value="(.*)"'
    re_match = re.match(pattern, text, re.S)

    if re_match:
        return re_match.group(1)
    else:
        return ''


def zhihu_login(account, password):
        phone_pattern = r'^\d{9,10}$'

        post_url = ''

        post_data = dict()
        post_data['password'] = password
        post_data['_xsrf'] = get_csrf()
        post_data['captcha'] = get_captcha()

        if re.match(phone_pattern, account):
            post_url ='https://www.zhihu.com/login/phone_num'

            post_data['phone_num'] = account
        elif "@" in account:
            post_url ='https://www.zhihu.com/login/email'

            post_data['email'] = account

        response = session.post(post_url, post_data, headers=header)
        print(response.text)
        session.cookies.save()


# zhihu_login('5083088487', 'Zuoqian690712')
print(is_login())
get_index()
