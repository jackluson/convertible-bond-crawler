'''
Desc: 可转债数据入口
File: /main.py
Project: convertible-bond
File Created: Saturday, 23rd July 2022 9:09:56 pm
-----
Copyright (c) 2022 Camel Lu
'''
from datetime import datetime

from modules.output import output_with_prepare
from modules.store import store_database
from modules.backtest import backtest
from utils.index import plot
from strategy.multiple_factors import impl_multiple_factors


if __name__ == "__main__":
    input_value = input("请输入下列序号执行操作:\n \
            1.“输出到本地” \n \
            2.“存到数据库” \n \
            3.“回测” \n \
            4.“可视化” \n \
            5.“多因子策略回测” \n \
        输入：")
    if input_value == '1':
        date = datetime.now().strftime("%Y-%m-%d")
        # date = "2023-08-02"
        output_with_prepare(date)
    if input_value == '2':
        store_database()
    elif input_value == '3':
        backtest()
        plot()
    elif input_value == '4':
        plot()
    elif input_value == '5':
        file_dir = 'price=115_count=10_premium=15_premium_ratio=0.5_stdevry=35_max_price=130_open_rating=1_score_bemchmark=1dynamic=True/'
        # file_dir = 'liquidity_out/'
        parent_dir = './backtest/'
        impl_multiple_factors(
            is_predict=False,
            file_dir=file_dir,
            parent_dir=parent_dir,
            until_win=False
        )
