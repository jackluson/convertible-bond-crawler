'''
Desc:
File: /config.py
File Created: Saturday, 8th April 2023 5:32:59 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import json

from params import backtest_dir, head_count
from utils.json import get_mid_temperature_data

repair_flag_style = 'color:blue'
repair_ransom_style = 'color:red'
pre_ransom_style = 'color:Fuchsia'
# 要item字段一一对应,否则数据库插入顺序
rename_map = {
    'id': 'id',
    'cb_id': 'id',
    'cb_code': '可转债代码',
    'cb_name': '可转债名称',
    'stock_code': '股票代码',
    'stock_name': '股票名称',
    'industry': '行业',
    'price': '转债价格',
    'premium_rate': '转股溢价率',
    'stock_stdevry': '正股波动率',
    'cb_to_pb': '转股价格/每股净资产',
    'date_remain_distance': '距离到期时间',
    'date_return_distance': '距离回售时间',
    'rate_expire': '到期收益率',
    'rate_expire_aftertax': '税后到期收益率',
    'remain_to_cap': '转债剩余/市值比例',
    'is_repair_flag': '是否满足下修条件',
    'repair_flag_remark': '下修备注',
    'pre_ransom_remark': '预满足强赎备注',
    'is_ransom_flag': '是否满足强赎条件',
    'ransom_flag_remark': '强赎备注',

    'remain_amount': '剩余规模',
    'trade_amount': '成交额',
    'turnover_rate': '换手率',
    'market_cap': '股票市值',

    'last_price': '上期转债价格',
    'last_cb_percent': '较上期涨跌幅',
    'cb_percent': '转债涨跌幅',
    'stock_price': '股价',
    'stock_percent': '股价涨跌幅',
    'last_stock_price': '上期股价',
    'last_stock_percent': '较上期股价涨跌幅',
    'arbitrage_percent': '日内套利',
    'convert_stock_price': '转股价格',
    'pb': '市净率',
    'market': '市场',

    'remain_price': '剩余本息',
    'remain_price_tax': '税后剩余本息',

    'is_unlist': '未发行',
    'last_is_unlist': '上期未发行',
    'issue_date': '发行日期',
    'date_convert_distance': '距离转股时间',

    'rate_return': '回售收益率',

    'old_style': '老式双底',
    'new_style': '新式双底',
    'rating': '债券评级',
    'weight_score': '多因子得分',
}

is_backtest = True

out_dir = backtest_dir if is_backtest else f'./liquidity_out/'
summary_filename = f'summary.json'
strategy_list = [
    # {
    #     'name': '所有',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_listed_all',
    #     'head_count': 1000  # 设置一个大值,取所有
    # },
    # {
    #     'name': '所有除新债',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_listed_all_exclude_new',
    #     'head_count': 1000  # 设置一个大值,取所有
    # },
    # {
    #     'name': '到期保本',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_profit_due',
    #     'head_count': head_count,
    # },
    # {
    #     'name': '回售摸彩',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_return_lucky',
    #     'head_count': head_count,
    # },
    # {
    #     'name': '低价格低溢价',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_double_low',
    #     'head_count': head_count,
    # },
    # {
    #     'name': '三低转债',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_three_low',
    #     'head_count': head_count,
    # },
    # {
    #     'name': '下修博弈',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_downward_revise',
    #     'head_count': head_count,
    # },
    # {
    #     'name': '次新',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_disable_converte',
    #     'head_count': head_count,
    # },
    {
        'name': '多因子',
        'start': "2022-10-22",
        'filter_key': 'filter_multiple_factors',
        'head_count': head_count,
    }
]


real_mid_temperature_map = get_mid_temperature_data()

rating_map = {
    'C': 0.15,
    'CC-': 0.2,
    'CC': 0.25,
    'CC+': 0.3,
    'CCC-': 0.35,
    'CCC': 0.4,
    'CCC+': 0.45,
    'B-': 0.5,
    'B': 0.55,
    'B+': 0.6,
    'BB-': 0.65,
    'BB': 0.7,
    'BB+': 0.75,
    'BBB-': 0.8,
    'BBB': 0.85,
    'BBB+': 0.9,
    'A-': 0.95,
    'A': 1,
    'A+': 1,
    'AA-': 1,
    'AA': 1,
    'AA+': 1,
    'AAA': 1
}
