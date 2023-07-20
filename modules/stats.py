'''
Desc:
File: /statistics.py
File Created: Saturday, 15th July 2023 11:23:40 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
from datetime import datetime
import modules.filter as filter


def statistics(df):
    df_all = filter.filter_listed_all(df)
    df_all['turnover_rate'] = (
        df_all['trade_amount']/df_all['remain_amount'] * 100).round(2)
    mid_price = df_all['price'].median().round(2)
    avg_price = df_all['price'].mean().round(2)
    mid_premium_rate = df_all['premium_rate'].median().round(2)
    avg_premium_rate = df_all['premium_rate'].mean().round(2)
    mid_remain_amount = df_all['remain_amount'].median().round(2)
    min_remain_amount = df_all['remain_amount'].min()
    df_sort_amount = df_all.sort_values(
        by='trade_amount', ascending=False).head(10).reset_index()
    max_remain_amount = df_all['remain_amount'].max()
    avg_remain_amount = df_all['remain_amount'].mean().round(2)
    total_remain_amount = df_all['remain_amount'].sum().round(2)
    total_trade_amount = df_all['trade_amount'].sum().round(2)
    mid_trade_amount = df_all['trade_amount'].median().round(2)
    avg_trade_amount = df_all['trade_amount'].mean().round(2)
    max_trade_amount = df_all['trade_amount'].max()
    mid_turnover_rate = df_all['turnover_rate'].median().round(2)
    avg_turnover_rate = df_all['turnover_rate'].mean().round(2)

    mid_cb_percent = df_all['cb_percent'].median().round(2)
    avg_cb_percent = df_all['cb_percent'].mean().round(2)

    df_raise = df_all[df_all['cb_percent'] > 0]
    df_fall = df_all[df_all['cb_percent'] < 0]
    df_static = df_all[df_all['cb_percent'] == 0]
    mid_market_cap = df_all['market_cap'].median().round(2)
    avg_market_cap = df_all['market_cap'].mean().round(2)
    min_market_cap = df_all['market_cap'].min()
    max_market_cap = df_all['market_cap'].max()
    top_trade_amount_total = df_sort_amount['trade_amount'].sum().round(2)
    res = {
        'count': len(df_all),
        'raise_count': len(df_raise),
        'fall_count': len(df_fall),

        'mid_price': mid_price,
        'avg_price': avg_price,
        'mid_premium_rate': mid_premium_rate,
        'avg_premium_rate': avg_premium_rate,

        'avg_remain_amount': avg_remain_amount,
        'mid_remain_amount': mid_remain_amount,
        'total_remain_amount': total_remain_amount,

        'mid_cb_percent': mid_cb_percent,
        'avg_cb_percent': avg_cb_percent,

        'total_trade_amount': total_trade_amount,
        'top_trade_amount_total': top_trade_amount_total,
        'mid_trade_amount': mid_trade_amount,
        'avg_trade_amount': avg_trade_amount,
        'max_trade_amount': max_trade_amount,

        'mid_turnover_rate': mid_turnover_rate,
        'avg_turnover_rate': avg_turnover_rate,

    }
    return res
