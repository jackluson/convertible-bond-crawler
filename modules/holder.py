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


def save_holder():
    last_path = f'{out_dir}cb_list.xlsx'
    xls = pd.ExcelFile(last_path, engine='openpyxl')
    df_all_last = xls.parse("所有")
    df_all_last['可转债代码'] = df_all_last['可转债代码'].astype(str)
    path = os.getcwd() + '/data/holder.json'
    f_data = open(path, "r")
    all_map = json.loads(f_data.read())
    parser = JqkaParser()
    for index, item in df_all_last.iterrows():
        if True or item['可转债代码'] not in all_map.keys():
            code = item['可转债代码']
            market = item['市场']
            holder_list = parser.get_holder_list(code, market)
            df_holder_list = pd.DataFrame(holder_list)
            df_holder_list = df_holder_list.loc[(df_holder_list['radio'] > 5)]
            df_holder_list = df_holder_list.sort_values(
                by='radio', ascending=False, ignore_index=True)
            save_item = {
                'top_holder_list': holder_list,
                'name': item['可转债名称'],
                'over_5_list': df_holder_list.to_dict('records'),
                'over_5_total': df_holder_list['radio'].sum()
            }
            all_map[code] = save_item

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(all_map, f, ensure_ascii=False, indent=2)
        f.close()


if __name__ == '__main__':
    save_holder()
