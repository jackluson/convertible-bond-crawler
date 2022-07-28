'''
Desc:
File: /login.py
Project: utils
File Created: Saturday, 23rd July 2022 9:12:43 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import os
from dotenv import load_dotenv

from .cookies import set_cookies

load_dotenv()


def login(redirect_url, is_cookies_login=False):
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument('--headless')
    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(12000)
    """
    模拟登录,支持两种方式：
        1. 设置已经登录的cookie
        2. 输入账号，密码，验证码登录（验证码识别正确率30%，识别识别支持重试）
    """
    login_url = 'https://www.ninwin.cn/index.php?m=u&c=login'
    cookie_str = os.getenv('login_cookie')
    print("is_cookies_login", is_cookies_login)
    if is_cookies_login and cookie_str:
        target_url = redirect_url if redirect_url else login_url
        set_cookies(chrome_driver, target_url, cookie_str)
    else:
        # login_status = mock_login_site(
        #     chrome_driver, login_url, redirect_url)
        # if login_status:
        #     print('login success')
        # else:
        #     print('login fail')
        exit()
    return chrome_driver
