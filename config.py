'''
Desc:
File: /config.py
File Created: Saturday, 8th April 2023 5:32:59 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''

# 要item字段一一对应,否则数据库插入顺序
rename_map = {
    'cb_code': '可转债代码',
    'cb_name': '可转债名称',
    'stock_code': '股票代码',
    'stock_name': '股票名称',
    'price': '转债价格',
    'premium_rate': '转股溢价率',
    'cb_to_pb': '转股价格/每股净资产',
    'date_remain_distance': '距离到期时间',
    'date_return_distance': '距离回售时间',
    'rate_expire': '到期收益率',
    'rate_expire_aftertax': '税后到期收益率',
    'remain_to_cap': '转债剩余/市值比例',
    'is_repair_flag': '是否满足下修条件',
    'repair_flag_remark': '下修备注',
    'is_ransom_flag': '是否满足强赎条件',
    'ransom_flag_remark': '强赎备注',

    'remain_amount': '剩余规模',
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
    'id': 'id',
    'cb_id': 'id',
    'weight_score': '多因子得分',
}

head_count = 10
premium_bemchmark = 30
out_dir = f'./out_dynamic_{head_count}_premium_bemchmark_{premium_bemchmark}/'
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
    {
        'name': '低价格低溢价',
        'start': "2022-10-22",
        'filter_key': 'filter_double_low',
        'head_count': head_count,
    },
    # {
    #     'name': '三低转债',
    #     'start': "2022-10-22",
    #     'filter_key': 'filter_three_low',
    #     'head_count': head_count,
    # },
    # {
    #     'name': '转股期未到',
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

multiple_factors_config = {
    'benchmark_temperature': 30,  # 基准温度
    # 'real_temperature'
    'bond_ratio': 0.7,  # 债性系数
    'stock_ratio': 0.3,  # 股性系数
    'price_bemchmark': 115,  # 价格基准
    'premium_bemchmark': premium_bemchmark,  # 溢价率基准

    'stock_option_ratio': 0.3,  # 可转债期权系数 -- 用到期时间衡量, 减分项, 小于一年减分
    'stock_option_bemchmark_days': 360,  # 可转债期权基准天数
    'stock_remain_ratio': 0.3,  # 正股剩余市值系数
    'stock_remain_bemchmark_min': 3,  # 剩余市值加分项
    'stock_remain_bemchmark_max': 30,  # 剩余市值减分项
    'stock_remain_score_min': 0.6,  # 剩余市值最低分
    'stock_pb_ratio': 0.3,  # 正股PB系数 减分项, 小于1.5减分
    'pb_bemchmark': 1.5,  # 正股PB基准
    'pb_score_min': 0.6,  # 正股PB最低分
    'stock_market_cap_ratio': 0.1,  # 正股市值系数
    'stock_market_cap_bemchmark_min': 50,  # 正股市值加分项
    'stock_market_cap_bemchmark_max': 500,  # 正股市值减分项
    'stock_market_cap_score_min': 0.6,  # 正股市值最低分
    'stock_market_cap_score_max': 1.5,  # 正股市值最高分
}

real_temperature_map = {
    '2022-10-22': 25.67,
    '2022-11-05': 27.78,
    '2022-11-11': 27.78,
    '2022-11-19': 30.22,
    '2022-12-03': 31.96,
    '2022-12-10': 31.46,
    '2022-12-17': 28.69,
    '2022-12-23': 22.39,
    '2022-12-31': 24.07,
    '2023-01-06': 27.43,
    '2023-01-14': 28.39,
    '2023-01-20': 32.66,
    '2023-02-04': 37.08,
    '2023-02-11': 38.35,
    '2023-02-18': 36.63,
    '2023-02-25': 38.69,
    '2023-03-04': 39.35,
    '2023-03-11': 37.02,
    '2023-03-19': 35.68,
    '2023-03-25': 38.4,
    '2023-04-01': 36.58,
    '2023-04-08': 36.59
}
