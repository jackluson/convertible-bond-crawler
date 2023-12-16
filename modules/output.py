'''
Desc:
File: /output.py
File Created: Saturday, 15th July 2023 1:03:41 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
import os
import json
import pandas as pd
from datetime import datetime
import modules.filter as filter
from modules.source import crawler
from modules.stats import statistics
from utils.json import write_fund_json_data, get_stock_info
from utils.index import output_excel
from config import (is_backtest, main_financial_map, out_dir, output_stats_list, output_stats_map,
    real_mid_temperature_map, rename_map, strategy_list, summary_filename)
from params import multiple_factors_config
from modules.fetch import fetch_indictor
from infra.sql.stocks.query import StockQuery
from infra.utils.enum import Freq
from infra.redis.anchor_plan_redis import get_anchor_plan_redis

pd.options.mode.chained_assignment = None


def set_dynamic_props(*, real_mid_price=None, real_temperature=None):
    is_dynamic_temperature = multiple_factors_config.get(
        "is_dynamic_temperature")
    is_dynamic_mid_price = multiple_factors_config.get(
        "is_dynamic_mid_price")
    if is_dynamic_mid_price and real_mid_price:
        multiple_factors_config['real_mid_price'] = real_mid_price
    if is_dynamic_temperature and real_temperature:
        multiple_factors_config['real_temperature'] = real_temperature
        if multiple_factors_config.get("is_dynamic_ratio"):
            benchmark_temperature = multiple_factors_config.get(
                'benchmark_temperature')
            stock_ratio = multiple_factors_config.get('stock_ratio')
            real_stock_ratio = round(
                stock_ratio * (1 - (real_temperature - benchmark_temperature) / benchmark_temperature), 2)
            real_bond_ratio = round(
                1 - multiple_factors_config.get('liquidity_ratio') - real_stock_ratio, 2)
            multiple_factors_config['real_stock_ratio'] = real_stock_ratio
            multiple_factors_config['real_bond_ratio'] = real_bond_ratio


def add_data(list, date, compare_date):
    last_map = {}
    code_stdevry_map = get_stock_info(date)
    stock_query = StockQuery()
    stock_pe_pb_list = stock_query.query_stock_pe_pb(date)
    code_dict = {}
    for item in stock_pe_pb_list:
        code_dict[item['code']] = item
        
    period_quarter_dict = pd.Timestamp(date).to_period(freq=Freq.QUARTER.value)
    last_quarter_end = (period_quarter_dict.start_time - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    main_financial_stock_list = stock_query.query_stock_main_financial(report_date=last_quarter_end)
    stock_main_financial_dict = {}
    for item in main_financial_stock_list:
        stock_main_financial_dict[item['code']] = item

    stock_quote_list = stock_query.query_stock_quote(date)
    stock_quote_dict = {}
    for item in stock_quote_list:
        stock_quote_dict[item['code']] = item
        
    path = os.getcwd() + '/data/holder.json'
    f_data = open(path, "r")
    all_map = json.loads(f_data.read())
    xls = None
    if date != compare_date:
        last_path = f'{out_dir}{compare_date}_cb_list.xlsx'
        xls = pd.ExcelFile(last_path, engine='openpyxl')
        df_all_last = xls.parse("All_ROW")
        df_all_last['可转债代码'] = df_all_last['可转债代码'].astype(str)
        for index, item in df_all_last.iterrows():
            last_map[item['可转债代码']] = item.to_dict()
    new_list = []
    for index in range(len(list)):
        item = list[index]
        stock_code = item['stock_code']
        price = item['price']
        stock_price = item['stock_price']
        cb_code = item['cb_code']
        item_stock = code_stdevry_map.get(
            stock_code, {})
        item_stock_pe_pb = code_dict.get(
            stock_code, {})
        item_stock_main_financial = stock_main_financial_dict.get(
            stock_code, {})
        item_stock_quote = stock_quote_dict.get(
            stock_code, {})
        circulating_amount = item.get('remain_amount')
        if item.get("date_convert_distance") != '已到':
            if all_map.get(cb_code):
                limited_ratio = all_map.get(cb_code).get('limited_ratio')
                limited_ratio = limited_ratio if limited_ratio else all_map.get(cb_code).get(
                    'over_5_total')
                circulating_amount = round(
                    (100 - limited_ratio) * circulating_amount * 0.01, 2)
            else:
                print(f'未找到{cb_code}, {item["cb_name"]}的持仓信息')
        merge_item = {
            **item_stock_quote,
            **item_stock_pe_pb,
            **item_stock_main_financial,
            **item,
            **item_stock,
            'pb': float(item_stock_quote.get("pb", item.get('pb'))), # 原来pb有一定错误概率
            'circulating_amount': circulating_amount,
        }
        new_item = dict()
        for key in rename_map.keys():
            if key in main_financial_map:
                val = merge_item.get(key)
                if 'yoy' in key and val:
                    val = val * 100
                if 'net_asset' == key and val and merge_item.get('total_shares') and merge_item.get('navps'):
                    # 总股本 * 每股净资产
                    val = (merge_item.get('total_shares') * merge_item.get('navps')) / (10 ** 8)
                new_item[key] =  round(val,2) if val else None
            else:
                new_item[key] = merge_item.get(key)

        last_record = last_map.get(cb_code)
        new_item['last_is_unlist'] = item['is_unlist'] if date == compare_date else "Y"
        if last_record:
            new_item['last_price'] = last_record.get(
                rename_map.get('price'))
            new_item['last_stock_price'] = last_record.get(
                rename_map.get('stock_price'))
            new_item['last_stock_percent'] = round((float(stock_price) - last_record.get(
                rename_map.get('stock_price')))/last_record.get(rename_map.get('stock_price'))*100, 2)
            new_item['last_cb_percent'] = round((float(price) - last_record.get(
                rename_map.get('price')))/last_record.get(rename_map.get('price'))*100, 2)
            new_item['last_is_unlist'] = last_record.get(
                rename_map.get("is_unlist"))
        # del new_item['id']
        # del new_item['cb_id']
        # del new_item['arbitrage_percent']
        new_list.append(new_item)
    return {
        'list': new_list,
        'last_xls': xls
    }


def output(*, date, compare_date, is_stats=True):
    list = crawler(date=date)
    res = add_data(list, date, compare_date)
    data_list = res.get('list')
    last_xls = res.get('last_xls')
    anchor_redis = get_anchor_plan_redis()
    df = pd.DataFrame.from_records(data_list)
    all_stats_info = None
    if is_stats:
        stats_list = []
        for item in output_stats_list:
            lte = item.get('lte')
            gt = item.get('gt')
            key = item.get('key')
            if item.get('lte') == None and item.get('gt') == None:
                stats_df = df
            elif lte != None and gt == None:
                stats_df = df[df[key] <= lte]
            elif lte != None and gt != None:
                stats_df = df[(df[key] <= lte) & (df[key] > gt)]
            elif gt != None:
                stats_df = df[df[key] > gt]
            # print(stats_df)
            stats_df.to_csv(f"stats/details/{item.get('title')}.csv",
                            header=True, index=True)
            len_df = len(stats_df)
            stats_df = filter.filter_listed_all(stats_df)

            if len_df > 0:
                title = item.get('title')
                stats_info = statistics(stats_df, title)
                if  len_df == len(df) and not all_stats_info:
                    all_stats_info = stats_info
                stats_dict = {
                    'title': title,
                    **stats_info
                }
                stats_list.append(stats_dict)

        df_stats_list = pd.DataFrame.from_records(stats_list)
        df_stats_list = df_stats_list.rename(columns=output_stats_map)
        df_stats_list.set_index('标题', inplace=True)
        df_stats_list.to_csv(f"stats/{date}.csv", header=True, index=True)
        source_path = f"stats/{date}.csv"
        dest_path = f'stats/lastest.csv'
        os.system(f'cp {source_path} {dest_path}')
    if multiple_factors_config.get(
            "is_dynamic_temperature"):
        print(
            f"        当前股市温度为: {multiple_factors_config['real_temperature']}")
        if multiple_factors_config.get("is_dynamic_ratio"):
            print(
                f"当前real_stock_ratio为: {multiple_factors_config['real_stock_ratio']}")
            print(
                f" 当前real_bond_ratio为: {multiple_factors_config['real_bond_ratio']} \n")

    all_stats_info = all_stats_info if all_stats_info else statistics(df, "所有")
    show_log(all_stats_info, date)
    top_10 = df.sort_values(
        by='trade_amount', ascending=False).head(10)
    selected_columns = ['cb_code', 'cb_name', 'price', 'premium_rate', 'cb_percent', 'stock_percent',
                        'remain_amount', 'date_convert_distance', 'date_remain_distance', 'stock_name', 'market_cap', 'industry', 'trade_amount', 'turnover_rate']
    print(top_10[selected_columns].set_index('cb_code'))
    # if not multiple_factors_config.get('real_mid_price'):
    multiple_factors_config['real_mid_price'] = float(stats_info.get('mid_price'))

    multiple_factors_config['real_mid_turnover_rate'] = float(stats_info.get(
        'mid_turnover_rate'))
    output_excel(df, sheet_name='All_ROW', date=date)
    df['over_mid_turnover_rate'] = df.apply(lambda x: 1 if x.turnover_rate >= float(stats_info.get(
        'mid_turnover_rate')) else 0, axis=1)
    filter_data_dict = {}
    for strategy in strategy_list:
        strategy_name = strategy['name']
        filter_key = strategy['filter_key']
        is_cache = strategy.get('is_cache')
        cache_data = anchor_redis.get_convertible_bond_filter_result(key=filter_key) if is_cache else None
        if cache_data:
            filter_data = pd.DataFrame.from_records(cache_data)
            filter_data_dict[filter_key] = filter_data
        else:
            filter_processor = getattr(filter, filter_key)
            if filter_key == 'filter_multiple_factors':
                filter_data = filter_processor(
                    df, date=date, multiple_factors_config=multiple_factors_config)
            else:
                filter_data = filter_processor(
                    df, multiple_factors_config=multiple_factors_config)
        print(f"{strategy_name}的数量：{len(filter_data)}只")
        output_excel(filter_data, sheet_name=strategy_name, date=date)
        filter_data_dict[filter_key] = filter_data
        if is_cache:
            anchor_redis.set_convertible_bond_filter_result(filter_key, filter_data.to_dict("records"))
    if date == compare_date:
        print('success!!! data total: ', len(list))
        filename = "multiple_factors_config.json"
        file_dir = f'{out_dir}'
        pathname = file_dir + filename
        write_fund_json_data(multiple_factors_config, filename, file_dir)
        return
    all_df_rename = df.rename(columns=rename_map).reset_index()
    percents = []
    for strategy in strategy_list:
        start = strategy['start']
        if start == date:
            continue
        strategy_name = strategy['name']
        head_count = strategy['head_count']
        all_last_strategy_df = last_xls.parse(strategy['name'])
        all_last_strategy_df['可转债代码'] = all_last_strategy_df['可转债代码'].astype(
            str)
        last_strategy_df = all_last_strategy_df.head(
            head_count)  # 读取前20条
        cur_percent = 0
        cur_stocks_percent = 0
        if len(last_strategy_df) > 0:
            last_strategy_df = pd.merge(all_df_rename, last_strategy_df,
                                        on=['可转债代码'], how='inner')
            cur_percent = round(last_strategy_df["较上期涨跌幅_x"].mean().round(
                2) * (len(last_strategy_df) / head_count), 2)  # 乘以仓位
            cur_stocks_percent = round(last_strategy_df["较上期股价涨跌幅_x"].mean().round(
                2) * (len(last_strategy_df) / head_count), 2)
        strategy['percent'] = cur_percent
        strategy['stocks_percent'] = cur_stocks_percent

        percents.append({
            'name': f'{strategy_name}(距{compare_date})',
            'total': len(all_last_strategy_df),
            'head': len(last_strategy_df),
            'percent': strategy['percent'],
            'stocks_percent': strategy['stocks_percent'],
        })
    filename = summary_filename
    file_dir = f'{out_dir}'
    pathname = file_dir + filename
    if not os.path.exists(pathname):
        stats_data = dict()
    else:
        with open(pathname) as json_file:
            stats_data = json.load(json_file)
    last_period_percents = stats_data.get(
        compare_date) if stats_data.get(compare_date) else []
    for strategy in strategy_list:
        last_accumulate_item = dict()
        start = strategy['start']
        if start == date:
            continue
        for percent in last_period_percents:
            if percent['name'] == f'累计{strategy["name"]}({start}至今)':
                last_accumulate_item = percent
        last_accumulate = last_accumulate_item.get(
            'percent') if last_accumulate_item.get('percent') else 0
        last_stocks_accumulate = last_accumulate_item.get(
            'stocks_percent') if last_accumulate_item.get('stocks_percent') else 0
        percents.append({
            'name': f'累计{strategy["name"]}({start}至今)',
            'percent': round(((last_accumulate / 100 + 1) * (1 + strategy.get('percent') / 100) - 1) * 100, 2),
            'stocks_percent': round(((last_stocks_accumulate / 100 + 1) * (1 + strategy.get('stocks_percent') / 100) - 1) * 100, 2)
        })
    stats_data[date] = percents
    write_fund_json_data(stats_data, filename, file_dir)
    output_excel(pd.DataFrame(percents), sheet_name="汇总", date=date)
    source_path = f'{out_dir}{date}_cb_list.xlsx'
    dest_path = f'{out_dir}cb_list.xlsx'
    os.system(f'cp {source_path} {dest_path}')


def prepare_config(date):
    compare_date = None
    date_keys = list(real_mid_temperature_map.keys())
    cur_mid_temperature = real_mid_temperature_map.get(date)
    # The above code is declaring a variable named "cur_mid_temperature".
    if cur_mid_temperature and compare_date == None:
        compare_date = date_keys[-2]
    else:
        compare_date = date_keys[-1]
    real_mid_price = cur_mid_temperature.get(
        'mid_price') if cur_mid_temperature else None
    real_temperature = cur_mid_temperature.get(
        'temperature') if cur_mid_temperature else None
    if real_temperature == None:
        data = fetch_indictor()
        real_temperature = float(data.get('median_pb_temperature'))
        print("real_temperature", real_temperature)
    set_dynamic_props(real_mid_price=real_mid_price,
                      real_temperature=real_temperature)
    return {
        'compare_date': compare_date
    }


def show_log(stats_info, date):
    mid_price = stats_info['mid_price']
    avg_price = stats_info['avg_price']
    mid_premium_rate = stats_info['mid_premium_rate']
    avg_premium_rate = stats_info['avg_premium_rate']
    mid_cb_value = stats_info['mid_cb_value']
    avg_cb_value = stats_info['avg_cb_value']
    count = stats_info['count']
    raise_count = stats_info['raise_count']
    fall_count = stats_info['fall_count']
    mid_cb_percent = stats_info['mid_cb_percent']
    avg_cb_percent = stats_info['avg_cb_percent']

    total_trade_amount = stats_info['total_trade_amount']
    max_trade_amount = stats_info['max_trade_amount']
    mid_trade_amount = stats_info['mid_trade_amount']
    avg_trade_amount = stats_info['avg_trade_amount']
    top_trade_amount_total = stats_info['top_trade_amount_total']

    mid_turnover_rate = stats_info['mid_turnover_rate']
    avg_turnover_rate = stats_info['avg_turnover_rate']

    mid_remain_amount = stats_info['mid_remain_amount']
    avg_remain_amount = stats_info['avg_remain_amount']
    total_remain_amount = stats_info['total_remain_amount']
    print(f"\n{date}统计数据:\n")
    print(f'  价格中位数: {mid_price}       价格平均数: {avg_price}')
    print(f'  溢价中位数: {mid_premium_rate}%        溢价平均数: {avg_premium_rate}%\n')
    print(f'转股价值中位数: {mid_cb_value}%  转股价值平均数: {avg_cb_value}%\n')
    print(
        f'  可转债数量: {count}只            涨跌比: {raise_count}/{fall_count} ')
    print(
        f'  涨幅中位数: {mid_cb_percent}%        涨幅平均数: {avg_cb_percent}% \n')

    print(f'成交量中位数: {mid_trade_amount}亿     成交量平均数: {avg_trade_amount}亿')
    print(f'换手率中位数: {mid_turnover_rate}%      换手率平均数: {avg_turnover_rate}%')
    print(
        f'  成交量总数: {total_trade_amount}亿     最大成交量: {max_trade_amount}亿      前十成交量之和: {top_trade_amount_total}亿')
    print(
        f'  余额中位数: {mid_remain_amount}亿       余额平均数: {avg_remain_amount}亿             总余额: {total_remain_amount}亿 \n')


def output_with_prepare(date=None):
    if date == None:
        date = datetime.now().strftime("%Y-%m-%d")
        # date = "2023-07-14"
    res = prepare_config(date)
    compare_date = res.get('compare_date')
    print(f"当前日期：{date}, 上期日期：{compare_date}")
    output(date=date, compare_date=compare_date, is_stats=~is_backtest)


if __name__ == "__main__":
    output_with_prepare()
