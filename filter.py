'''
Desc:
File: /filter.py
File Created: Sunday, 9th April 2023 4:10:19 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
from datetime import datetime


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
        & ((df['premium_rate'] < 30) | (df['price'] < 130))
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
    """多因子筛选
    债权+股权
    1. 价格
    2. 溢价率
    3. 剩余市值
    4. 正股市值
    5. 到期时间
    6. 波动率
    """

    benchmark_temperature = multiple_factors_config.get(
        "benchmark_temperature")
    mid_price_bemchmark = multiple_factors_config.get(
        "mid_price_bemchmark")
    bond_ratio = multiple_factors_config.get("bond_ratio")  # 债性系数
    stock_ratio = multiple_factors_config.get("stock_ratio")

    price_bemchmark = multiple_factors_config.get('price_bemchmark')  # 价格基准

    premium_bemchmark = multiple_factors_config.get(
        'premium_bemchmark')  # 溢价率基准

    premium_ratio = multiple_factors_config.get(
        'premium_ratio')
    stock_option_ratio = multiple_factors_config.get(
        'stock_option_ratio')  # 可转债期权系数 -- 用到期时间衡量, 减分项, 小于一年减分
    stock_option_bemchmark_days = multiple_factors_config.get(
        "stock_option_bemchmark_days")  # 可转债期权基准天数
    remain_ratio = multiple_factors_config.get(
        'remain_ratio')  # 正股剩余市值系数
    remain_bemchmark_min = multiple_factors_config.get(
        "remain_bemchmark_min")  # 剩余市值加分项
    remain_bemchmark_max = multiple_factors_config.get(
        "remain_bemchmark_max")  # 剩余市值减分项
    remain_score_min = multiple_factors_config.get(
        "remain_score_min")  # 剩余市值最低分

    stock_pb_ratio = multiple_factors_config.get(
        "stock_pb_ratio")  # 正股PB系数 减分项, 小于1.5减分
    pb_bemchmark = multiple_factors_config.get("pb_bemchmark")  # 正股PB基准
    pb_score_min = multiple_factors_config.get("pb_score_min")  # 正股PB最低分

    stock_market_cap_ratio = multiple_factors_config.get(
        "stock_market_cap_ratio")  # 正股市值系数
    stock_market_cap_bemchmark_min = multiple_factors_config.get(
        "stock_market_cap_bemchmark_min")  # 正股市值加分项
    stock_market_cap_bemchmark_max = multiple_factors_config.get(
        "stock_market_cap_bemchmark_max")  # 正股市值减分项
    stock_market_cap_score_min = multiple_factors_config.get(
        "stock_market_cap_score_min")  # 正股市值最低分
    stock_market_cap_score_max = multiple_factors_config.get(
        "stock_market_cap_score_max")  # 正股市值最高分

    stock_stdevry_ratio = multiple_factors_config.get(
        'stock_stdevry_ratio')  # 正股剩余市值系数
    stock_stdevry_bemchmark = multiple_factors_config.get(
        "stock_stdevry_bemchmark")  # 波动率基准
    # 正股波动率最高分
    stock_stdevry_score_max = multiple_factors_config.get(
        "stock_stdevry_score_max")

    stock_stdevry_score_min = multiple_factors_config.get(
        "stock_stdevry_score_min")  # 正股波动率最低分

    max_price = multiple_factors_config.get("max_price")  # 最高价
    df_filter = df.loc[
        (df['date_return_distance'] != '无权')
        & (df['is_unlist'] == 'N')
        & (~df["cb_name"].str.contains("EB"))
        & (df['is_ransom_flag'] == 'False')
        & (df['cb_to_pb'] > 0.5)  # 排除问题债
        & (df['cb_to_pb'] < 15)  # 排除问题债
    ]
    weight_score_key = 'weight'

    def core_filter(row):
        # if weight_score > 1:
        #     return True
        if '天' in row.date_remain_distance and not '年' in row.date_remain_distance:
            day_count = float(row.date_remain_distance[0:-1])
            return day_count > 90 and row[weight_score_key] > 1
        if row.price > max_price:
            return False
        # if '后可能满足强赎条件' in row.pre_ransom_remark and row.price >= 141:
        #     return False
        return row[weight_score_key] > 1

    def calulate_score(row):
        # 股权基础分
        premium_score = 1 - (row.premium_rate -
                             premium_bemchmark) / premium_bemchmark
        # 债权基础分
        price_score = 1 - (row.price - price_bemchmark) / \
            price_bemchmark
        # mid_price_score =
        # 可转债股性市净率评分
        pb_score = round(
            min(1, max(pb_score_min, 1 - (pb_bemchmark - row.pb) / pb_bemchmark)), 2)
        # 可转债股性期权评分
        date_format = '%Y-%m-%d'  # 日期格式
        issue_date = datetime.strptime(row.issue_date, date_format)
        now_date = datetime.strptime(date, date_format)
        # 计算两个日期之间的天数
        days_remain = 365 * 6 - (now_date - issue_date).days
        stock_option_score = 1
        if days_remain < stock_option_bemchmark_days:
            stock_option_score = round(1 -
                                       (stock_option_bemchmark_days - days_remain) /
                                       stock_option_bemchmark_days, 2)
        # 可转债股性剩余市值评分
        remain_score = 1
        if row.remain_amount < remain_bemchmark_min:
            remain_score = round(1 -
                                 (row.remain_amount - remain_bemchmark_min) /
                                 remain_bemchmark_min, 2)
        elif row.remain_amount > remain_bemchmark_max:
            remain_score = max(remain_score_min, round(1 -
                                                       (row.remain_amount - remain_bemchmark_max) /
                                                       remain_bemchmark_max, 2))
        # 可转债股性正股市值评分
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
        # 正股波动率评分
        stock_stdevry_score = round(
            1 - (stock_stdevry_bemchmark - row.stock_stdevry) / stock_stdevry_bemchmark, 2)

        stock_stdevry_score = min(
            stock_stdevry_score_max, max(stock_stdevry_score_min, stock_stdevry_score))

        bond_score = round(price_score * bond_ratio, 2)

        stock_score = round(stock_ratio *
                            (
                                premium_score * premium_ratio +
                                stock_stdevry_score * stock_stdevry_ratio +
                                remain_score * remain_ratio +
                                pb_score * stock_pb_ratio +
                                stock_option_score * stock_option_ratio +
                                stock_market_cap_score * stock_market_cap_ratio
                            ), 2)

        row['option'] = stock_option_score
        row['remain'] = remain_score
        row['pb_score'] = pb_score
        row['stdevry'] = stock_stdevry_score
        row['stock_market_cap'] = stock_market_cap_score
        row['bond'] = bond_score
        row['stock'] = stock_score
        weight_score = bond_score + stock_score
        row[weight_score_key] = weight_score
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
