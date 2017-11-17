import hashlib
import datetime
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


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
