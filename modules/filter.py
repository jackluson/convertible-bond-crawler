'''
Desc:
File: /filter.py
File Created: Sunday, 9th April 2023 4:10:19 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
from datetime import datetime
from config import rating_map


def filter_profit_due(df):
    df_filter = df.loc[(df['rate_expire_aftertax'] > 0)
                       #    & (df['price'] < 115)
                       & (df['date_convert_distance'] == '已到')
                       & (df['cb_to_pb'] > 1.5)
                       & (df['is_repair_flag'] == 'True')
                       #    & (df['remain_to_cap'] > 5)
                       ]

    def my_filter(row):
        if '暂不行使下修权利' in row.repair_flag_remark or '距离不下修承诺' in row.repair_flag_remark:
            return False
        return True
    df_filter = df_filter[df_filter.apply(my_filter, axis=1)]
    return df_filter


def filter_return_lucky(df):
    df_filter = df.loc[(df['price'] < 125)
                       & (df['rate_expire_aftertax'] > -10)
                       & (df['date_return_distance'] == '回售内')
                       & (~df["cb_name"].str.contains("EB"))
                       & (df['cb_to_pb'] > (1 + df['premium_rate'] * 0.008))
                       & (df['is_repair_flag'] == 'True')
                       & (df['remain_to_cap'] > 5)
                       ]
    df_filter = df_filter.sort_values(
        by='new_style', ascending=True, ignore_index=True)
    return df_filter


def filter_double_low(df):
    df_filter = df.loc[(df['date_return_distance'] != '无权')
                       & (~df["cb_name"].str.contains("EB"))
                       & (df['is_unlist'] == 'N')
                       #    & (df['date_return_distance'] != '回售内')
                       & (df['is_ransom_flag'] == 'False')
                       & (df['cb_to_pb'] > 0.5)
                       & (df['remain_to_cap'] > 5)
                       & (((df['price'] < 128)
                           & (df['premium_rate'] < 10)) | ((df['price'] < 125)
                                                           & (df['premium_rate'] < 15)))
                       ]

    def due_filter(row):
        if '天' in row.date_remain_distance and not '年' in row.date_remain_distance:
            day_count = float(row.date_remain_distance[0:-1])
            return day_count > 90
        return True
    df_filter = df_filter[df_filter.apply(due_filter, axis=1)]

    df_filter = df_filter.sort_values(
        by='new_style', ascending=True, ignore_index=True)
    return df_filter


def filter_three_low(df):
    df_filter = df.loc[
        (~df["cb_name"].str.contains("EB"))
        #    & (df['date_return_distance'] != '回售内')
        & (df['is_ransom_flag'] == 'False')
        & (df['cb_to_pb'] > 0.5)
        & (df['remain_amount'] < 2)
        & ((df['premium_rate'] < 30) | (df['price'] < 145))
        & (df['market_cap'] < 100)
    ]

    def due_filter(row):
        if '天' in row.date_remain_distance and not '年' in row.date_remain_distance:
            day_count = float(row.date_remain_distance[0:-1])
            return day_count > 90
        return True
    df_filter = df_filter[df_filter.apply(due_filter, axis=1)]

    df_filter = df_filter.sort_values(
        by='remain_amount', ascending=True, ignore_index=True)
    return df_filter


def filter_disable_converte(df):
    df_filter = df.loc[
        (~df["cb_name"].str.contains("EB"))
        & (df['date_convert_distance'] != '已到')
        & (df['is_unlist'] == 'N')
        & (df['last_is_unlist'] == 'N')
    ]

    df_filter = df_filter.sort_values(
        by='remain_amount', ascending=True, ignore_index=True)
    return df_filter


def filter_multiple_factors(df, *, date, multiple_factors_config):
    benchmark_temperature = multiple_factors_config.get(
        "benchmark_temperature")
    mid_price_bemchmark = multiple_factors_config.get(
        "mid_price_bemchmark")
    bond_ratio = multiple_factors_config.get("bond_ratio")  # 债性系数
    stock_ratio = multiple_factors_config.get("stock_ratio")
    liquidity_ratio = multiple_factors_config.get("liquidity_ratio")
    score_bemchmark = multiple_factors_config.get("score_bemchmark")

    price_bemchmark = multiple_factors_config.get('price_bemchmark')  # 价格基准
    is_dynamic_mid_price = multiple_factors_config.get('is_dynamic_mid_price')
    real_price_bemchmark = price_bemchmark
    if is_dynamic_mid_price:
        real_mid_price = multiple_factors_config.get("real_mid_price")
        mid_price_ratio = 1 - ((real_mid_price - mid_price_bemchmark) /
                               mid_price_bemchmark)
        mid_price_ratio = round(mid_price_ratio, 2)
        real_price_bemchmark = round(
            price_bemchmark * mid_price_ratio, 2)  # 实时价格基准
        print('real_price_bemchmark:', real_price_bemchmark)

    premium_bemchmark = multiple_factors_config.get(
        'premium_bemchmark')  # 溢价率基准
    real_premium_bemchmark = multiple_factors_config.get(
        'premium_bemchmark')  # 溢价率基准
    is_dynamic_temperature = multiple_factors_config.get(
        'is_dynamic_temperature')
    if is_dynamic_temperature:
        real_temperature = multiple_factors_config.get("real_temperature")
        temperature_ratio = 1 - ((real_temperature - benchmark_temperature) /
                                 benchmark_temperature)
        temperature_ratio = round(temperature_ratio, 2)
        real_premium_bemchmark = round(
            real_premium_bemchmark * temperature_ratio, 2)
        print('real_premium_bemchmark:', real_premium_bemchmark)
        is_dynamic_ratio = multiple_factors_config.get("is_dynamic_ratio")
        if is_dynamic_ratio:
            bond_ratio = multiple_factors_config.get(
                "real_bond_ratio")  # 动态债性系数
            stock_ratio = multiple_factors_config.get(
                "real_stock_ratio")  # 动态股性系数
    stock_option_bemchmark_days = multiple_factors_config.get(
        "stock_option_bemchmark_days")  # 可转债期权基准天数

    remain_bemchmark_min = multiple_factors_config.get(
        "remain_bemchmark_min")  # 剩余市值加分项
    remain_bemchmark_max = multiple_factors_config.get(
        "remain_bemchmark_max")  # 剩余市值减分项
    remain_score_min = multiple_factors_config.get(
        "remain_score_min")  # 剩余市值最低分

    pb_bemchmark = multiple_factors_config.get("pb_bemchmark")  # 正股PB基准
    pb_score_min = multiple_factors_config.get("pb_score_min")  # 正股PB最低分

    stock_market_cap_bemchmark_min = multiple_factors_config.get(
        "stock_market_cap_bemchmark_min")  # 正股市值加分项
    stock_market_cap_bemchmark_max = multiple_factors_config.get(
        "stock_market_cap_bemchmark_max")  # 正股市值减分项
    stock_market_cap_score_min = multiple_factors_config.get(
        "stock_market_cap_score_min")  # 正股市值最低分
    stock_market_cap_score_max = multiple_factors_config.get(
        "stock_market_cap_score_max")  # 正股市值最高分
    stock_stdevry_bemchmark = multiple_factors_config.get(
        "stock_stdevry_bemchmark")  # 波动率基准
    # 正股波动率最高分
    stock_stdevry_score_max = multiple_factors_config.get(
        "stock_stdevry_score_max")

    stock_stdevry_score_min = multiple_factors_config.get(
        "stock_stdevry_score_min")  # 正股波动率最低分

    max_price = multiple_factors_config.get("max_price")  # 最高价\

    df_filter = df.loc[
        (df['date_return_distance'] != '无权')
        & (df['is_unlist'] == 'N')
        & (~df["cb_name"].str.contains("EB"))
        & (df['is_ransom_flag'] == 'False')
        & (df['cb_to_pb'] > 0.5)  # 排除问题债
        & (df['price'] < max_price)  # 排除问题债
    ]
    real_mid_turnover_rate = multiple_factors_config.get(
        'real_mid_turnover_rate')
    if multiple_factors_config.get('open_turnover_rate'):
        df_filter = df_filter.loc[(
            df_filter['turnover_rate'] >= real_mid_turnover_rate)]  # 是否开启换手率过滤
    weight_score_key = 'weight'

    def core_filter(row):
        # if weight_score > 1:
        #     return True
        if '天' in row.date_remain_distance and not '年' in row.date_remain_distance:
            day_count = float(row.date_remain_distance[0:-1])
            return day_count > 90 and row[weight_score_key] > 1
        # if '后可能满足强赎条件' in row.pre_ransom_remark and row.price >= 141:
        #     return False
        return row[weight_score_key] > score_bemchmark

    def calulate_score(row):
        # 债性因子
        # 债性因子 - 价格
        bond_price_score = 1 - (row.price - real_price_bemchmark) / \
            real_price_bemchmark

        # 债性因子 - 剩余规模
        bond_remain_score = 1
        if row.remain_amount < remain_bemchmark_min:
            bond_remain_score = round(1 -
                                      (row.remain_amount - remain_bemchmark_min) /
                                      remain_bemchmark_min, 2)
        elif row.remain_amount > remain_bemchmark_max:
            bond_remain_score = max(remain_score_min, round(1 -
                                                            (row.remain_amount - remain_bemchmark_max) /
                                                            remain_bemchmark_max, 2))
        # 债性因子 - 剩余时间（期权）
        date_format = '%Y-%m-%d'  # 日期格式
        issue_date = datetime.strptime(row.issue_date, date_format)
        now_date = datetime.strptime(date, date_format)
        # 计算两个日期之间的天数
        days_remain = 365 * 6 - (now_date - issue_date).days
        stock_option_score = 1
        if days_remain < stock_option_bemchmark_days:
            stock_option_score = round(
                days_remain / stock_option_bemchmark_days, 2)
        # 股性因子
        # 股性因子 - 价格
        stock_premium_score = 1 - (row.premium_rate -
                                   real_premium_bemchmark) / premium_bemchmark
        # 股性因子 - 正股市值
        stock_market_cap_score = 1
        if row.market_cap < stock_market_cap_bemchmark_min:
            stock_market_cap_score = round(1 -
                                           (row.market_cap - stock_market_cap_bemchmark_min) /
                                           stock_market_cap_bemchmark_min, 2)
        elif row.market_cap > stock_market_cap_bemchmark_max:
            stock_market_cap_score = round(1 -
                                           (row.market_cap - stock_market_cap_bemchmark_max) /
                                           stock_market_cap_bemchmark_max, 2)

        stock_market_cap_score = min(stock_market_cap_score_max, max(
            stock_market_cap_score_min, stock_market_cap_score))
        # 股性因子 -- 正股波动率
        stock_stdevry_score = round(
            1 - (stock_stdevry_bemchmark - row.stock_stdevry) / stock_stdevry_bemchmark, 2)

        stock_stdevry_score = min(
            stock_stdevry_score_max, max(stock_stdevry_score_min, stock_stdevry_score))
        # 股性因子 - 正股PB
        stock_pb_score = round(
            min(1, max(pb_score_min, 1 - (pb_bemchmark - row.pb) / pb_bemchmark)), 2)

        # 流动性

        cur_turnover_rate = row.turnover_rate
        denominator = cur_turnover_rate if cur_turnover_rate >= real_mid_turnover_rate else real_mid_turnover_rate
        liquidity_turnover_rate_score = 1 + \
            (cur_turnover_rate - real_mid_turnover_rate) / \
            denominator * 0.1

        liquidity_turnover_rate_score = min(
            multiple_factors_config.get('liquidity_turnover_score_max'), max(multiple_factors_config.get('liquidity_turnover_score_min'), liquidity_turnover_rate_score))
        # 综合计算
        rating_ratio = rating_map.get(
            row.rating) if multiple_factors_config.get('open_rating') else 1
        bond_score = round(
            bond_price_score * multiple_factors_config.get('bond_price_ratio') * rating_ratio +
            bond_remain_score * multiple_factors_config.get('bond_remain_ratio'), 2)

        stock_score = round(
            stock_premium_score * multiple_factors_config.get('stock_premium_ratio') +
            stock_market_cap_score * multiple_factors_config.get('stock_market_cap_ratio') +
            stock_stdevry_score * multiple_factors_config.get('stock_stdevry_ratio') +
            stock_pb_score * multiple_factors_config.get('stock_pb_ratio') +
            stock_option_score *
            multiple_factors_config.get('stock_option_ratio'),
            2)
        liquidity_score = 0
        if liquidity_ratio > 0:
            liquidity_score = liquidity_turnover_rate_score * \
                multiple_factors_config.get('liquidity_turnover_rate_ratio')
            liquidity_score = round(liquidity_score * liquidity_ratio, 3)
            row['liquidity'] = liquidity_score
        row['stock'] = round(stock_score * stock_ratio, 3)
        row['bond'] = round(bond_score * bond_ratio, 3)
        weight_score = liquidity_score + row['stock'] + row['bond']
        row[weight_score_key] = weight_score
        row['bond_price'] = round(
            bond_price_score * multiple_factors_config.get('bond_price_ratio') * rating_ratio * bond_ratio, 3)
        row['bond_remain'] = round(
            bond_remain_score * multiple_factors_config.get('bond_remain_ratio') * bond_ratio, 3)

        row['stock_premium'] = round(
            stock_premium_score * multiple_factors_config.get('stock_premium_ratio') * stock_ratio, 3)

        return row
    df_filter = df_filter.apply(calulate_score, axis=1)
    df_filter = df_filter[df_filter.apply(core_filter, axis=1)]

    df_filter = df_filter.sort_values(
        by=weight_score_key, ascending=False, ignore_index=True)
    return df_filter


def filter_listed_all(df):
    df_filter = df.loc[
        (~df["cb_name"].str.contains("EB"))
        & (df['is_unlist'] == 'N')
    ]
    return df_filter


def filter_listed_all_exclude_new(df):
    df_filter = df.loc[
        (~df["cb_name"].str.contains("EB"))
        & (df['is_unlist'] == 'N')
        & (df['last_is_unlist'] == 'N')
    ]
    return df_filter


def filter_downward_revise(df):
    df_filter = df.loc[
        (df['cb_to_pb'] > 1.2)
        & (~df["cb_name"].str.contains("EB"))
        & (df['date_convert_distance'] == '已到')
        & (~df["repair_flag_remark"].str.contains("暂不行使下修权利"))
        & (~df["repair_flag_remark"].str.contains("距离不下修承诺"))
        & (df["price"] < 118)
        & (df["premium_rate"] > 40)
    ]
    df_filter = df_filter.sort_values(
        by='new_style', ascending=True, ignore_index=True)
    return df_filter


def filter_candidate(df):
    df_filter = df.loc[
        (df['cb_to_pb'] > 1.2)
        & (df['is_unlist'] == 'N')
        & (~df["cb_name"].str.contains("EB"))
        & (df["price"] < 130)
        & (df["premium_rate"] < 30)
        & (df["turnover_rate"] > 2)
    ]

    def due_filter(row):
        if '年' in row.date_remain_distance and row.date_remain_distance[0] != '0':
            return True
        return False
    df_filter = df_filter[df_filter.apply(due_filter, axis=1)]

    df_filter = df_filter.sort_values(
        by='remain_amount', ascending=True, ignore_index=True)
    return df_filter
