'''
Desc:
File: /params.py
File Created: Saturday, 15th July 2023 11:03:33 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''

head_count = 10
premium_bemchmark = 15
stdevry_bemchmark = 35
liquidity_ratio = 0
stock_ratio = 0.3
bond_ratio = round(1 - liquidity_ratio - stock_ratio, 2)
price_bemchmark = 115
premium_ratio = 0.5
max_price = 130
open_rating = 1
open_turnover_rate = True
score_bemchmark = 1
is_dynamic = True

backtest_dir = f'./backtest/stock_ratio={stock_ratio}_price={price_bemchmark}_count={head_count}_premium={premium_bemchmark}_premium_ratio={premium_ratio}_stdevry={stdevry_bemchmark}_max_price={max_price}_open_rating={open_rating}_score_bemchmark={score_bemchmark}_dynamic={is_dynamic}/'


summary_filename = f'summary.json'

multiple_factors_config = {
    'benchmark_temperature': 50,  # 基准温度
    # 'real_temperature'
    'bond_ratio': bond_ratio,  # 债性系数
    'stock_ratio': stock_ratio,  # 股性系数
    'liquidity_ratio': liquidity_ratio,  # 流动性系数
    'price_bemchmark': price_bemchmark,  # 价格基准
    'is_dynamic_temperature': is_dynamic,
    'mid_price_bemchmark': 115,  # 中位数价格基准
    'is_dynamic_mid_price': is_dynamic,
    'is_dynamic_ratio': is_dynamic,
    # 'real_mid_price':
    # 债性因子
    'bond_price_ratio': 0.7,
    'bond_remain_ratio': 0.3,  # 可转债剩余市值系数
    'remain_bemchmark_min': 3,  # 剩余规模加分项
    'remain_bemchmark_max': 10,  # 剩余规模减分项
    'remain_score_min': 0.5,  # 剩余市值最低分
    # 股性因子
    'stock_premium_ratio': premium_ratio,  # 溢价率系数
    'stock_market_cap_ratio': 0.2,  # 正股市值系数
    'stock_stdevry_ratio': 0.1,  # 正股波动率系数
    'stock_pb_ratio': 0.1,  # 正股PB系数 减分项, 小于1.5减分
    'stock_option_ratio': 0.1,  # 可转债期权系数 -- 用到期时间衡量, 减分项, 小于一年减分
    'stock_option_bemchmark_days': 720,  # 可转债期权基准天数
    'premium_bemchmark': premium_bemchmark,  # 溢价率基准
    'stock_market_cap_bemchmark_min': 30,  # 正股市值加分项
    'stock_market_cap_bemchmark_max': 100,  # 正股市值减分项
    'stock_market_cap_score_min': 0.5,  # 正股市值最低分
    'stock_market_cap_score_max': 1.5,  # 正股市值最高分
    'stock_stdevry_bemchmark': stdevry_bemchmark,  # 波动率基准
    'stock_stdevry_score_min': 0.5,  # 正股波动率最低分
    'stock_stdevry_score_max': 1.5,  # 正股波动率最高分
    'pb_bemchmark': 1.5,  # 正股PB基准
    'pb_score_min': 0.5,  # 正股PB最低分
    # 流动性因子
    'liquidity_turnover_rate_ratio': 1,  # 换手率系数
    'liquidity_turnover_score_min': 0.5,  # 最低分
    'liquidity_turnover_score_max': 2,  # 正股波动率最高分
    # 'real_mid_turnover_rate'
    'open_rating': open_rating,
    'open_turnover_rate': open_turnover_rate,
    # 过滤项
    'max_price': max_price,  # 最高价
    'score_bemchmark': score_bemchmark  # 最小多因子分数
}
