'''
Desc: check current holdings and buy/sell
File: /check.py
File Created: Saturday, 3rd December 2022 12:52:23 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''

import json
from datetime import datetime
import pandas as pd
import numpy as np


def get_last_holds():
    history_filepath = './history.json'
    f_history = open(history_filepath, "r")
    history_list = json.loads(f_history.read())
    last_holds = history_list[-1]
    return last_holds


def archive_hold_list():
    buy_sell_filepath = 'buy_sell.json'
    f_buy_sell = open(buy_sell_filepath, "r")
    history_filepath = './history.json'
    f_history = open(history_filepath, "r")

    data_buy_sell = json.loads(f_buy_sell.read())
    history_list = json.loads(f_history.read())
    last_holds = history_list[-1]

    date_keys = list(data_buy_sell.keys())
    target_key = date_keys[-1]
    cur_buy_sell = data_buy_sell.get(target_key)
    cur_buys = cur_buy_sell.get('buy')
    print("target_key", target_key)
    cur_holds = []
    cur_sell_keys = []
    for item in cur_buy_sell.get('sell'):
        cur_sell_keys.append(item.get('code'))
    for item in last_holds.get('holdlist'):
        if not item.get('code') in cur_sell_keys:
            cur_holds.append(item)
    cur_holds = [*cur_holds, *cur_buys]

    history_list.append({'date': target_key, 'holdlist': cur_holds})

    with open(history_filepath, 'w', encoding='utf-8') as f:
        json.dump(history_list, f, ensure_ascii=False, indent=2)
        f.close()


def check():
    date = datetime.now().strftime("%Y-%m-%d")
    path = './out/' + date + '_cb_list.xlsx'
    xls = pd.ExcelFile(path, engine='openpyxl')
    df_all = None
    for sheet_name in xls.sheet_names:
        if sheet_name != 'All':
            df_cur_sheet = xls.parse(sheet_name)
            # print('<------' + sheet_name + '------>')
            if type(df_all) is pd.DataFrame:
                df_all = df_all.append(df_cur_sheet)
            else:
                df_all = df_cur_sheet
    code_list = df_all['可转债代码'].apply(str).to_list()
    last_hold_list = get_last_holds().get('holdlist')
    print('以下转债不在策略之外, 但目前持有:视情况可卖出:\n')
    for hold_item in last_hold_list:
        if hold_item.get('code') not in code_list:
            print(hold_item.get('code'), hold_item.get('name'))


def check_no_hold():
    date = datetime.now().strftime("%Y-%m-%d")
    path = './out/' + date + '_cb_list.xlsx'
    xls = pd.ExcelFile(path, engine='openpyxl')
    df_all = None
    for sheet_name in xls.sheet_names:
        if sheet_name != 'All':
            df_cur_sheet = xls.parse(sheet_name)
            # print('<------' + sheet_name + '------>')
            if type(df_all) is pd.DataFrame:
                df_all = df_all.append(df_cur_sheet)
            else:
                df_all = df_cur_sheet
    last_hold_list = get_last_holds().get('holdlist')
    code_hold_list = []
    for hold_item in last_hold_list:
        code_hold_list.append(hold_item.get('code'))
    print('以下转债在策略中,但暂未持有:视情况可买入:\n')
    results = []
    for index, item in df_all.iterrows():
        if str(item['可转债代码']) not in code_hold_list and (item['下修备注'] is np.nan or '暂不行使下修' not in item['下修备注']):
            results.append(item)
    df_result = pd.DataFrame(results)
    df_result = df_result[['可转债代码', '可转债名称', '转债价格',
                          '距离回售时间', '距离到期时间', '转股溢价率', '转债剩余/市值比例']].reset_index(drop=True)
    print(df_result)


if __name__ == "__main__":
    opt = int(input("请输入下列序号执行操作:\n \
        1: check 出队列表. \n \
        2: check 入队列表.\n \
        3: 归档持仓列表.\n \
    输入："))
    if opt == 1:
        check()
    elif opt == 2:
        check_no_hold()
    elif opt == 3:
        archive_hold_list()
