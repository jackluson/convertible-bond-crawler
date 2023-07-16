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
from config import rename_map, strategy_list, out_dir, summary_filename, real_mid_temperature_map
from params import multiple_factors_config

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
            stock_code) if code_stdevry_map.get(stock_code) else dict()
        merge_item = {
            **item,
            **item_stock,
        }
        new_item = dict()
        for key in rename_map.keys():
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
        del new_item['id']
        del new_item['cb_id']
        new_list.append(new_item)
    return {
        'list': new_list,
        'last_xls': xls
    }


def output(*, date, compare_date):
    list = crawler(date=date)
    res = add_data(list, date, compare_date)
    data_list = res.get('list')
    last_xls = res.get('last_xls')
    df = pd.DataFrame.from_records(data_list)
    stats_info = statistics(df)
    show_log(stats_info, date)
    # if not multiple_factors_config.get('real_mid_price'):
    multiple_factors_config['real_mid_price'] = stats_info.get('mid_price')

    multiple_factors_config['real_mid_turnover_rate'] = stats_info.get(
        'mid_turnover_rate')
    output_excel(df, sheet_name='All_ROW', date=date)
    filter_data_dict = {}
    for strategy in strategy_list:
        strategy_name = strategy['name']
        filter_key = strategy['filter_key']
        filter_processor = getattr(filter, filter_key)
        if filter_key == 'filter_multiple_factors':
            filter_data = filter_processor(
                df, date=date, multiple_factors_config=multiple_factors_config)
        else:
            filter_data = filter_processor(df)
        print(f"{strategy_name}的数量：{len(filter_data)}只")
        output_excel(filter_data, sheet_name=strategy_name, date=date)
        filter_data_dict[filter_key] = filter_data
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
        real_temperature = 32.79
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
    print(f'  价格中位数: {mid_price}      价格平均数: {avg_price}')
    print(f'  溢价中位数: {mid_premium_rate}%        溢价平均数: {avg_premium_rate}%\n')
    print(
        f'  可转债数量: {count}只            涨跌比: {raise_count}/{fall_count} ')
    print(
        f'  涨幅中位数: {mid_cb_percent}%       涨幅平均数: {avg_cb_percent}% \n')

    print(f'成交量中位数: {mid_trade_amount}亿     成交量平均数: {avg_trade_amount}亿')
    print(f'换手率中位数: {mid_turnover_rate}%      换手率平均数: {avg_turnover_rate}%')
    print(
        f'  成交量总数: {total_trade_amount}亿     最大成交量: {max_trade_amount}亿     前十成交量之和: {top_trade_amount_total}亿')
    print(
        f'  余额中位数: {mid_remain_amount}亿       余额平均数: {avg_remain_amount}亿      总余额: {total_remain_amount}亿 \n')

    if multiple_factors_config.get(
            "is_dynamic_temperature"):
        print(
            f"        当前股市温度为: {multiple_factors_config['real_temperature']}")
        if multiple_factors_config.get("is_dynamic_ratio"):
            print(
                f"当前real_stock_ratio为: {multiple_factors_config['real_stock_ratio']}")
            print(
                f" 当前real_bond_ratio为: {multiple_factors_config['real_bond_ratio']} \n")


def output_with_prepare(date=None):
    if date == None:
        # date = datetime.now().strftime("%Y-%m-%d")
        date = "2023-07-14"
    res = prepare_config(date)
    compare_date = res.get('compare_date')
    print(f"当前日期：{date}, 上期日期：{compare_date}")
    output(date=date, compare_date=compare_date)


if __name__ == "__main__":
    output_with_prepare()
