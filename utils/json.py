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


def get_mid_temperature_data(path='mid_temperature.json'):
    f_data = open(path, "r")
    return json.loads(f_data.read())


def get_stock_info(date):
    filename = f'stdevry_{date}.json'
    # filename = f'stdevry.json'
    file_dir = os.getcwd() + f'/out/stdevry/'
    code_stdevry_map = dict()
    if not os.path.exists(file_dir + filename):
        filename = f'stdevry.json'
    with open(file_dir + filename) as json_file:
        code_stdevry_map = json.load(json_file)
    return code_stdevry_map
