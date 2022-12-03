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


def get_last_holds():
    history_filepath = './history.json'
    f_history = open(history_filepath, "r")
    history_list = json.loads(f_history.read())
    last_holds = history_list[-1]
    return last_holds


def make_history_list():
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
            print('<------' + sheet_name + '------>')
            if type(df_all) is pd.DataFrame:
                df_all = df_all.append(df_cur_sheet)
            else:
                df_all = df_cur_sheet
    code_list = df_all['可转债代码'].apply(str).to_list()
    last_hold_list = get_last_holds().get('holdlist')
    for hold_item in last_hold_list:
        if hold_item.get('code') not in code_list:
            print(hold_item.get('code'), hold_item.get('name'))


if __name__ == "__main__":
    is_check = 1
    if is_check:
        check()
    else:
        make_history_list()
