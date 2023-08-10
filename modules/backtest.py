'''
Desc:
File: /backtest.py
File Created: Sunday, 16th July 2023 6:55:52 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
import os

from modules.output import output, set_dynamic_props
from params import multiple_factors_config
from config import real_mid_temperature_map


def backtest():
    htmlFiles = os.listdir('./html/')
    dateList = []
    for file in htmlFiles:
        dateList.append(file[0:10])
    sorted_dates = sorted(dateList)
    prev_date = None
    for idx, date in enumerate(sorted_dates):
        cur_date = date
        compare_date = prev_date if prev_date else sorted_dates[
            0] if idx == 0 else sorted_dates[idx-1]
        print(idx, cur_date, compare_date)
        # last_path = f'{out_dir}{compare_date}_cb_list.xlsx'
        # if idx != 0 and not os.path.exists(last_path):
        #     continue
        is_dynamic_temperature = multiple_factors_config.get(
            "is_dynamic_temperature")
        is_dynamic_mid_price = multiple_factors_config.get(
            "is_dynamic_mid_price")
        cur_mid_temperature = real_mid_temperature_map.get(cur_date)
        if cur_mid_temperature == None:
            print(f"{cur_date}的市场温度或者中间价不存在")
            continue
        real_mid_price = None
        if is_dynamic_mid_price:
            real_mid_price = cur_mid_temperature.get('mid_price')
            if real_mid_price == None:
                print(f"{cur_date}的中位数价格不存在")
                continue
        real_temperature = None
        if is_dynamic_temperature:
            real_temperature = cur_mid_temperature.get('temperature')
            if real_temperature == None:
                print(f"{cur_date}的市场温度不存在")
                continue
        if is_dynamic_temperature or is_dynamic_mid_price:
            set_dynamic_props(real_mid_price=real_mid_price,
                              real_temperature=real_temperature)
        output(date=date, compare_date=compare_date, is_stats=False)
        prev_date = cur_date  # 成功输出之后，更新prev_date
