'''
Desc:
File: /connect.py
Project: utils
File Created: Sunday, 24th July 2022 10:38:55 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''

import os

import pymysql
from dotenv import load_dotenv


def connect():
    load_dotenv()
    env_db_host = os.getenv('db_host')
    env_db_name = os.getenv('db_name')
    env_db_user = os.getenv('db_user')
    env_db_password = os.getenv('db_password')
    connect = pymysql.connect(
        host=env_db_host, user=env_db_user, password=env_db_password, db=env_db_name,
        charset='utf8')
    connect_dict = {
        'connect': connect,
        'cursor_tuple': connect.cursor(),
        'cursor': connect.cursor(pymysql.cursors.DictCursor)
    }
    return connect_dict


if __name__ == '__main__':
    connect()
