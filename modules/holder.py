'''
Desc:
File: /holder.py
File Created: Sunday, 17th September 2023 11:09:38 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
import os
import pandas as pd
from infra.parser.jqka import JqkaParser
import json
from config import (is_backtest, out_dir)
from infra.api.eastmoney import ApiEastMoney


def save_holder():
    last_path = f'{out_dir}cb_list.xlsx'
    xls = pd.ExcelFile(last_path, engine='openpyxl')
    df_all_last = xls.parse("所有")
    df_all_last['可转债代码'] = df_all_last['可转债代码'].astype(
        str).apply(lambda x: x.zfill(6))
    path = os.getcwd() + '/data/holder.json'
    f_data = open(path, "r")
    all_map = json.loads(f_data.read())
    parser = JqkaParser()
    for index, item in df_all_last.iterrows():
        date_convert_distance = item['距离转股时间']
        code = item['可转债代码']
        if code not in all_map.keys() and date_convert_distance != '已到':
            stock_code = item['股票代码']
            market = item['市场']
            holder_list = parser.get_holder_list(code, market)
            df_holder_list = pd.DataFrame(holder_list)
            df_holder_list = df_holder_list.loc[(df_holder_list['radio'] > 5)]
            df_holder_list = df_holder_list.sort_values(
                by='radio', ascending=False, ignore_index=True)
            save_item = {
                'top_holder_list': holder_list,
                'name': item['可转债名称'],
                'stock_code': str(stock_code).zfill(6),
                'over_5_list': df_holder_list.to_dict('records'),
                'over_5_total': df_holder_list['radio'].sum().round(2),
                'date_convert_distance': date_convert_distance
            }
            all_map[code] = save_item
        elif item['可转债代码'] in all_map.keys():
            save_item = {
                **all_map[code],
                'date_convert_distance': date_convert_distance
            }
            all_map[code] = save_item

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(all_map, f, ensure_ascii=False, indent=2)
        f.close()


def save_yzxdr():
    last_path = f'{out_dir}cb_list.xlsx'
    xls = pd.ExcelFile(last_path, engine='openpyxl')
    df_all_last = xls.parse("All_ROW")
    df_all_last['股票代码'] = df_all_last['股票代码'].astype(
        str).apply(lambda x: x.zfill(6))
    path = os.getcwd() + '/data/yzxdr.json'
    f_data = open(path, "r")
    all_map = json.loads(f_data.read())
    api = ApiEastMoney()

    for index, item in df_all_last.iterrows():
        if item['距离转股时间'] != '已到' and item['股票代码'] not in all_map.keys():
            code = item['股票代码']
            list = api.get_yzxdr(code)
            print("list", list)
            save_item = {
                'list': list,
                'stock_name': item['股票名称'],
                'name': item['可转债名称'],
            }
            all_map[code] = save_item
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(all_map, f, ensure_ascii=False, indent=2)
        f.close()


def calc_limited_ratio():
    path_holder = os.getcwd() + '/data/holder.json'
    f_data = open(path_holder, "r")
    all_holder_map = json.loads(f_data.read())
    path_yzxdr = os.getcwd() + '/data/yzxdr.json'
    f_data = open(path_yzxdr, "r")
    all_yzxdr_map = json.loads(f_data.read())
    for key in all_holder_map:
        stock_code = all_holder_map[key].get('stock_code')
        item_yzxdr = all_yzxdr_map.get(stock_code)
        if not item_yzxdr:
            continue
        yzxdr_list = item_yzxdr.get('list')
        top_holder_list = all_holder_map.get(key).get('top_holder_list')
        limited_ratio = all_holder_map.get(key).get('over_5_total')
        for item in yzxdr_list:
            item_ratio = item.get('SHAREHDRATIO')
            item_name = item.get('SHAREHDNAME')
            # 小于5%的 并且在十大股东中才计入
            if item_ratio <= 5:
                flag = False
                for item_holder in top_holder_list:
                    if item_holder.get('name') == item_name:
                        flag = True
                        break
                if flag == True:
                    limited_ratio += item_ratio
        # if limited_ratio != all_holder_map[key].get('limited_ratio'):
        #     print('stock_code', stock_code)
        save_item = {
            **all_holder_map[key],
            'limited_ratio': round(limited_ratio, 2),
        }
        all_holder_map[key] = save_item
    with open(path_holder, 'w', encoding='utf-8') as f:
        json.dump(all_holder_map, f, ensure_ascii=False, indent=2)
        f.close()


if __name__ == '__main__':
    calc_limited_ratio()
    # save_holder()
