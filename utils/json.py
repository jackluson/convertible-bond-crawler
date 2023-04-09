'''
Desc:
File: /json.py
File Created: Saturday, 8th April 2023 5:30:33 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import os
import json


def write_fund_json_data(data, filename, file_dir=None):
    if not file_dir:
        # cur_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        file_dir = os.getcwd() + '/data/json/'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
        print("目录新建成功：%s" % file_dir)
    with open(file_dir + filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.close()
