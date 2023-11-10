'''
Desc:
File: /config.py
File Created: Saturday, 8th April 2023 5:32:59 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''

from params import backtest_dir, head_count
from utils.json import get_mid_temperature_data

repair_flag_style = 'color:blue'
repair_ransom_style = 'color:red'
pre_ransom_style = 'color:Fuchsia'
# 要item字段一一

save_database_map = {
    'id': 'id',
    'cb_id': 'id',
    'cb_code': '可转债代码',
    'cb_name': '可转债名称',
    'stock_code': '股票代码',
    'stock_name': '股票名称',
    
    'price': '转债价格',
    'premium_rate': '转股溢价率',
    'cb_percent': '转债涨跌幅',
    'stock_percent': '股价涨跌幅',
    'pb': '市净率',
    'cb_to_pb': '转股价格/每股净资产',
    
    'cb_value': '转股价值',
    'remain_amount': '剩余规模',
    'trade_amount': '成交额',
    'market_cap': '股票市值',
    
    'date_remain_distance': '距离到期时间',
    'date_return_distance': '距离回售时间',
    'rate_expire': '到期收益率',
    'rate_expire_aftertax': '税后到期收益率',
    'rate_return': '回售收益率',
    'remain_to_cap': '转债剩余/市值比例',
    'is_repair_flag': '是否满足下修条件',
    'repair_flag_remark': '下修备注',
    'pre_ransom_remark': '预满足强赎备注',
    'is_ransom_flag': '是否满足强赎条件',
    'ransom_flag_remark': '强赎备注',
    
    'stock_price': '股价',
    'arbitrage_percent': '日内套利',
    'convert_stock_price': '转股价格',
    'market': '市场',

    'remain_price': '剩余本息',
    'remain_price_tax': '税后剩余本息',

    'is_unlist': '未发行',
    'issue_date': '发行日期',
    'date_convert_distance': '距离转股时间',

    'old_style': '老式双底',
    'new_style': '新式双底',
    'rating': '债券评级',
}

main_financial_map = {
    'total_revenue_yoy': '营收同比%',
    'net_profit_atsopc_yoy': '净利润同比%',
    'net_profit_after_nrgal_atsolc_yoy': '扣非净利润同比%',
    'net_selling_rate': '净利率',
    'gross_selling_rate': '毛利率',
    'roe': 'ROE',
    'asset_liab_ratio': '资产负债率',
    'net_asset': '净资产',
    'goodwill_in_net_assets': '商誉占比%',
}

rename_map = {
    # 'id': 'id',
    # 'cb_id': 'id',
    'cb_code': '可转债代码',
    'cb_name': '可转债名称',
    'stock_code': '股票代码',
    'stock_name': '股票名称',
     # 简介（不存数据库）
    'industry': '行业',
    'classi_name': '企业性质',
    'provincial_name': '省份',
    'main_operation_business': '主营业务',
    
    'price': '转债价格',
    'premium_rate': '转股溢价率',
    'cb_percent': '转债涨跌幅',
    'stock_percent': '股价涨跌幅',
    'stock_stdevry': '正股波动率',
    'market_cap': '股票市值',
    'remain_amount': '剩余规模',
    'circulating_amount': '流通规模',
    'trade_amount': '成交额',
    'turnover_rate': '换手率',
    
    # 估值水位字段
    'pb': 'PB',
    'pb_percent': 'pb水位',
    'pe': 'PE',
    'pe_percent': 'pe水位',
    'pe_koufei': '扣非PE',
    'pe_koufei_percent': '扣非PE水位',
    **main_financial_map,
    
    
    'cb_value': '转股价值',
    'cb_to_pb': '转股价格/每股净资产',
    
    'date_remain_distance': '距离到期时间',
    'date_return_distance': '距离回售时间',
    'rate_expire': '到期收益率',
    'rate_expire_aftertax': '税后到期收益率',
    'rate_return': '回售收益率',
    'remain_to_cap': '转债剩余/市值比例',
    'is_repair_flag': '是否满足下修条件',
    'repair_flag_remark': '下修备注',
    'pre_ransom_remark': '预满足强赎备注',
    'is_ransom_flag': '是否满足强赎条件',
    'ransom_flag_remark': '强赎备注',


    'last_price': '上期转债价格',
    'last_cb_percent': '较上期涨跌幅',
    'stock_price': '股价',
    'last_stock_price': '上期股价',
    'last_stock_percent': '较上期股价涨跌幅',
    # 'arbitrage_percent': '日内套利',
    'convert_stock_price': '转股价格',
    # 'market': '市场',

    'remain_price': '剩余本息',
    'remain_price_tax': '税后剩余本息',

    'is_unlist': '未发行',
    'last_is_unlist': '上期未发行',
    'issue_date': '发行日期',
    'date_convert_distance': '距离转股时间',

    'old_style': '老式双底',
    'new_style': '新式双底',
    'rating': '债券评级',
    'weight': '多因子得分',

}

output_stats_map = {
    'title': '标题',
    'count': '总数量(只)',
    'raise_count': '上涨数量',
    'fall_count': '下跌数量',
    'mid_cb_percent': '涨跌幅中位数(%)',
    'avg_cb_percent': '涨跌幅平均数(%)',
    'mid_price': '中位数',
    'avg_price': '平均数',
    'mid_premium_rate': '溢价中位数(%)',
    'avg_premium_rate': '溢价平均数',
    'mid_remain_amount': '剩余规模中位数(亿)',
    'avg_remain_amount': '剩余规模平均数',
    'total_remain_amount': '总剩余规模',
    'mid_cb_value': '转股价值中位数',
    'avg_cb_value': '转股价值平均数',
    'total_trade_amount': '总成交额(亿)',
    'top_trade_amount_total': '前10成交额',
    'mid_trade_amount': '成交额中位数',
    'avg_trade_amount': '平均成交额',
    'max_trade_amount': '最大成交额',
    'mid_turnover_rate': '换手率中位数(%)',
    'avg_turnover_rate': '平均换手率',
}

output_stats_list = [
    {
        'title': '所有',
    },
    {
        'title': '<=100',
        'key': 'price',
        'lte': 100
    },
    {
        'title': '100~110',
        'key': 'price',
        'gt': 100,
        'lte': 110,
    },
    {
        'title': '110~120',
        'key': 'price',
        'gt': 110,
        'lte': 120,
    },
    {
        'title': '120~130',
        'key': 'price',
        'gt': 120,
        'lte': 130,
    },
    {
        'title': '130~150',
        'key': 'price',
        'gt': 130,
        'lte': 150,
    },
    {
        'title': '>150',
        'key': 'price',
        'gt': 150,
    },
    {
        'title': '溢价<=0',
        'key': 'premium_rate',
        'lte': 0,
    },
    {
        'title': '溢价0~10',
        'key': 'premium_rate',
        'gt': 0,
        'lte': 10,
    },
    {
        'title': '溢价10~20',
        'key': 'premium_rate',
        'gt': 10,
        'lte': 20,
    },
    {
        'title': '溢价20~30',
        'key': 'premium_rate',
        'gt': 20,
        'lte': 30,
    },
    {
        'title': '溢价30~40',
        'key': 'premium_rate',
        'gt': 30,
        'lte': 40,
    },
    {
        'title': '溢价40~50',
        'key': 'premium_rate',
        'gt': 40,
        'lte': 50,
    },
    {
        'title': '溢价50~70',
        'key': 'premium_rate',
        'gt': 50,
        'lte': 70,
    },
    {
        'title': '溢价>70',
        'key': 'premium_rate',
        'gt': 70,
    },
    {
        'title': '转股价值<=60',
        'key': 'cb_value',
        'lte': 60,
    },
    {
        'title': '转股价值60~80',
        'key': 'cb_value',
        'gt': 60,
        'lte': 80,
    },
    {
        'title': '转股价值80~90',
        'key': 'cb_value',
        'gt': 80,
        'lte': 90,
    },
    {
        'title': '转股价值90~100',
        'key': 'cb_value',
        'gt': 90,
        'lte': 100,
    },
    {
        'title': '转股价值100~110',
        'key': 'cb_value',
        'gt': 100,
        'lte': 110,
    },
    {
        'title': '转股价值110~120',
        'key': 'cb_value',
        'gt': 110,
        'lte': 120,
    },
    {
        'title': '转股价值>130',
        'key': 'cb_value',
        'gt': 130,
    },
    {
        'title': '规模<=1.5',
        'key': 'remain_amount',
        'lte': 1.5,
    },
    {
        'title': '规模1.5~3',
        'key': 'remain_amount',
        'gt': 1.5,
        'lte': 3,
    },
    {
        'title': '规模3~4',
        'key': 'remain_amount',
        'gt': 3,
        'lte': 4,
    },
    {
        'title': '规模4~5',
        'key': 'remain_amount',
        'gt': 4,
        'lte': 5,
    },
    {
        'title': '规模5~6',
        'key': 'remain_amount',
        'gt': 5,
        'lte': 6,
    },
    {
        'title': '规模6~8',
        'key': 'remain_amount',
        'gt': 6,
        'lte': 8,
    },
    {
        'title': '规模8~10',
        'key': 'remain_amount',
        'gt': 8,
        'lte': 10,
    },
    {
        'title': '规模10~20',
        'key': 'remain_amount',
        'gt': 10,
        'lte': 20,
    },
    {
        'title': '规模20~50',
        'key': 'remain_amount',
        'gt': 20,
        'lte': 50,
    },
    {
        'title': '规模>50',
        'key': 'remain_amount',
        'gt': 50,
    }
]

is_backtest = False

out_dir = backtest_dir if is_backtest else f'./strict_out/'
summary_filename = f'summary.json'
strategy_list = [{
    'name': '多因子',
    'start': "2022-10-22",
    'filter_key': 'filter_multiple_factors',
    'head_count': head_count,
}] if is_backtest else [
    {
        'name': '所有',
        'start': "2022-10-22",
        'filter_key': 'filter_listed_all',
        'head_count': 1000  # 设置一个大值,取所有
    },
    {
        'name': '所有除新债',
        'start': "2022-10-22",
        'filter_key': 'filter_listed_all_exclude_new',
        'head_count': 1000  # 设置一个大值,取所有
    },
    {
        'name': '低价格低溢价',
        'start': "2022-10-22",
        'filter_key': 'filter_double_low',
        'head_count': head_count,
    },
    {
        'name': '多因子',
        'start': "2022-10-22",
        'filter_key': 'filter_multiple_factors',
        'head_count': head_count,
    },
    {
        'name': '低水位',
        'start': "2023-11-09",
        'filter_key': 'filter_low_level_stock',
        'head_count': head_count,
    },
    {
        'name': '妖债基因',
        'start': "2022-10-22",
        'filter_key': 'filter_genie',
        'head_count': head_count,
    },
    {
        'name': '小规模不强赎',
        'start': "2022-10-22",
        'filter_key': 'filter_small_scale_not_ransom',
        'head_count': head_count,
    },
    {
        'name': '次新小规模',
        'start': "2022-10-22",
        'filter_key': 'filter_new_small',
        'head_count': head_count,
    },
    {
        'name': '候选圈',
        'start': "2022-10-22",
        'filter_key': 'filter_candidate',
        'head_count': head_count,
    },
    {
        'name': '下修博弈',
        'start': "2022-10-22",
        'filter_key': 'filter_downward_revise',
        'head_count': head_count,
    },
    {
        'name': '到期保本',
        'start': "2022-10-22",
        'filter_key': 'filter_profit_due',
        'head_count': head_count,
    },
    {
        'name': '回售摸彩',
        'start': "2022-10-22",
        'filter_key': 'filter_return_lucky',
        'head_count': head_count,
    },
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
