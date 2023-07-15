'''
Desc: 可转债数据入口
File: /main.py
Project: convertible-bond
File Created: Saturday, 23rd July 2022 9:09:56 pm
-----
Copyright (c) 2022 Camel Lu
'''
import os
import json
from modules.output import output, set_dynamic_props, output_with_prepare
from modules.store import store_database
from utils.index import plot
from config import real_mid_temperature_map
from params import multiple_factors_config
from strategy.multiple_factors import impl_multiple_factors


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
        output(date=date, compare_date=compare_date)
        prev_date = cur_date  # 成功输出之后，更新prev_date


if __name__ == "__main__":
    input_value = input("请输入下列序号执行操作:\n \
            1.“输出到本地” \n \
            2.“存到数据库” \n \
            3.“回测” \n \
            4.“可视化” \n \
            5.“多因子策略回测” \n \
        输入：")
    if input_value == '1':
        output_with_prepare()
    if input_value == '2':
        store_database()
    elif input_value == '3':
        backtest()
        plot()
    elif input_value == '4':
        plot()
    elif input_value == '5':
        file_dir = 'bond=0.7_stock=0.3_liquidity=0_price=115_count=10_premium=20_premium_ratio=0.5_stdevry=35_max_price=130_open_rating=1_score_bemchmark=1dynamic=True/'
        file_dir = 'liquidity_out/'
        parent_dir = './'
        impl_multiple_factors(
            is_predict=False,
            file_dir=file_dir,
            parent_dir=parent_dir,
            until_win=False
        )
