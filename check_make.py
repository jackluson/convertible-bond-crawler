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
    history_filepath = './log/position.json'
    f_history = open(history_filepath, "r")
    history_list = json.loads(f_history.read())
    last_holds = history_list[-1]
    return last_holds


def archive_hold_list():
    buy_sell_filepath = './log/trade.json'
    f_buy_sell = open(buy_sell_filepath, "r")
    history_filepath = './log/position.json'
    f_history = open(history_filepath, "r")
    date = datetime.now().strftime("%Y-%m-%d")
    data_path = './out/' + date + '_cb_list.xlsx'
    xls = pd.ExcelFile(data_path, engine='openpyxl')
    all_cb = xls.parse("All")
    all_cb_map = {}
    for index, item in all_cb.iterrows():
        all_cb_map[str(item['可转债代码'])] = item.to_dict()
    data_buy_sell = json.loads(f_buy_sell.read())
    history_list = json.loads(f_history.read())
    last_holds = history_list[-1]

    date_keys = list(data_buy_sell.keys())
    target_key = date_keys[-1]
    cur_buy_sell = data_buy_sell.get(target_key)
    cur_buys = cur_buy_sell.get('buy')
    cur_buys_details = []
    cur_holds = []
    cur_sell_keys = []
    for item in cur_buy_sell.get('sell'):
        cur_sell_keys.append(item.get('code'))
    for item in cur_buys:
        cur_cb = all_cb_map.get(item.get('code'))
        cur_buys_details.append({
            **item,
            'buy_price': cur_cb.get('转债价格'),
            'cur_price': cur_cb.get('转债价格'),
            "last_percent": cur_cb.get('较上期涨跌幅')
        })
    last_percent = 0
    radio_sum = 0
    for item in last_holds.get('holdlist'):
        # if not item.get('code') in cur_sell_keys:
        #     cur_holds.append(item)
        # else:
        flag = True
        cur_cb = all_cb_map.get(item.get('code'))
        for sell_item in cur_buy_sell.get('sell'):
            if sell_item.get('code') == item.get('code'):
                if sell_item.get("radio") > item.get('radio'):
                    raise BaseException('卖出超过持有仓位')
                elif sell_item.get("radio") < item.get('radio'):
                    cur_holds.append({
                        "code": sell_item.get("code"),
                        "name": sell_item.get("name"),
                        "radio": item.get('radio') - sell_item.get("radio"),
                        'cur_price': cur_cb.get('转债价格'),
                        "last_percent": cur_cb.get('较上期涨跌幅')
                    })
                flag = False
                break
        if flag == True:
            cur_holds.append({
                **item,
                'cur_price': cur_cb.get('转债价格'),
                'last_percent': cur_cb.get('较上期涨跌幅')
            })
        if cur_cb:
            last_percent = last_percent + \
                cur_cb.get('较上期涨跌幅') * item.get('radio')
            radio_sum = radio_sum + item.get('radio')

    cur_holds = [*cur_holds, *cur_buys_details]

    history_list.append({'date': target_key, 'last_percent': round(last_percent /
                        radio_sum, 2), 'holdlist': cur_holds})

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
            df_cur_sheet = xls.parse(sheet_name, dtype={
                "可转债代码": np.str,
            })
            # print('<------' + sheet_name + '------>')
            if type(df_all) is pd.DataFrame:
                df_all = df_all.append(df_cur_sheet)
            else:
                df_all = df_cur_sheet
    code_list = df_all['可转债代码'].apply(str).to_list()
    last_hold_list = get_last_holds().get('holdlist')
    print("last_hold_list", pd.DataFrame(last_hold_list))
    print('以下转债不在策略之外, 但目前持有:视情况可卖出:\n')
    for hold_item in last_hold_list:
        if hold_item.get('code') not in code_list:
            print(hold_item.get('code'), hold_item.get('name'))


def check_no_hold():
    date = datetime.now().strftime("%Y-%m-%d")
    path = './out/' + date + '_cb_list.xlsx'
    xls = pd.ExcelFile(path, engine='openpyxl')
    df_all = None
    exclude_sheet_names = ['到期保本', '回售摸彩', '低价格低溢价', ]
    for sheet_name in xls.sheet_names:
        if sheet_name in exclude_sheet_names:
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
        # print("item", item)
        remark = item['下修备注']
        if remark:
            remark = ''
        if str(item['可转债代码']) not in code_hold_list and (remark is np.nan or '暂不行使下修' not in remark):
            results.append(item)
    df_result = pd.DataFrame(results)
    df_result = df_result[['可转债代码', '可转债名称', '转债价格',
                          '距离回售时间', '距离到期时间', '转股溢价率', '转债剩余/市值比例', '税后到期收益率', "老式双底", "新式双底"]].reset_index(drop=True)
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
