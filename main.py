'''
Desc: 可转债数据入口
File: /main.py
Project: convertible-bond
File Created: Saturday, 23rd July 2022 9:09:56 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import time
from bs4 import BeautifulSoup

from utils.login import login


def main(is_read_local=False):

    # 利用BeautifulSoup解析网页源代码
    path = "output.html"
    bs = None
    if is_read_local:
        htmlfile = open(path, 'r', encoding='utf-8')
        bs = BeautifulSoup(htmlfile.read(), 'lxml')
        htmlfile.close()
    else:
        with open(path, "w", encoding='utf-8') as file:
            page_url = "https://www.ninwin.cn/index.php?m=cb&a=cb_all"
            chrome_driver = login(page_url, is_cookies_login=True)
            print("chrome_driver", chrome_driver)
            # 获取每页的源代码
            data = chrome_driver.page_source
            bs = BeautifulSoup(data, 'lxml')
            # prettify the soup object and convert it into a string
            file.write(str(bs.prettify()))
    print(bs)
    time.sleep(3600)


if __name__ == "__main__":
    main(True)
