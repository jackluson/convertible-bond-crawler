'''
Desc: 可转债数据入口
File: /main.py
Project: convertible-bond
File Created: Saturday, 23rd July 2022 9:09:56 pm
-----
Copyright (c) 2022 Camel Lu
'''
import os
import re
import string
import json
import time
from datetime import datetime
import pandas as pd
import filter
from lib.mysnowflake import IdWorker
from utils.index import get_bs_source, store_database, output_excel, delete_key_for_store, plot
from utils.json import write_fund_json_data
from config import is_backtest, rename_map, strategy_list, out_dir, summary_filename, multiple_factors_config
from strategy.multiple_factors import impl_multiple_factors
repair_flag_style = 'color:blue'
repair_ransom_style = 'color:red'
pre_ransom_style = 'color:Fuchsia'


def impl(is_output, is_save_database, *, date, compare_date):
    isReadLocal = False
    output_path = './html/' + date + "_output.html"
    print(f"上期时间为:{compare_date}")
    last_map = {}
    is_start = date == compare_date
    if is_start == False:
        last_path = f'{out_dir}{compare_date}_cb_list.xlsx'
        xls = pd.ExcelFile(last_path, engine='openpyxl')
        df_all_last = xls.parse("All_ROW")
        df_all_last['可转债代码'] = df_all_last['可转债代码'].astype(str)
        for index, item in df_all_last.iterrows():
            last_map[item['可转债代码']] = item.to_dict()
    filename = f'stdevry_{date}.json'
    # filename = f'stdevry.json'
    file_dir = os.getcwd() + f'/out/stdevry/'
    code_stdevry_map = dict()
    if not os.path.exists(file_dir + filename):
        filename = f'stdevry.json'
    with open(file_dir + filename) as json_file:
        code_stdevry_map = json.load(json_file)
    if os.path.exists(output_path):
        if os.path.getsize(output_path) > 0:
            isReadLocal = True
    bs = get_bs_source(date, isReadLocal)
    # print(bs)
    rows = bs.find_all('tr')
    list = []
    worker = IdWorker()
    for index in range(0, len(rows)):
        row = rows[index]
        try:
            # print(row)
            cb_id = row.get("data-id")  # 获取属性值
            cb_name = row.get("data-cb_name")
            cb_code = row.get("data-cbcode")
            stock_code = str(row.get("data-stock_code")[2:])
            market = row.get("data-stock_code")[0:2]
            stock_name = row.get("data-stock_name")
            price = row.get("data-cb_price")  # 可转债价格
            rating = row.get("data-rating")  # 债券评级
            cb_percent = row.find_all('td', {'class': "cb_mov2_id"})[
                0].get_text().strip()[0:-1]  # 转债涨幅
            cb_flags = row.find_all('td', {'class': "cb_name_id"})[
                0].find_all('span')  # 转债名称
            is_repair_flag = False
            repair_flag_remark = ''
            is_ransom_flag = False
            ransom_flag_remark = ''
            pre_ransom_remark = ''
            for flags in cb_flags:
                flag_style = flags.get('style').replace(' ', '')
                if flag_style == repair_flag_style:
                    is_repair_flag = True
                    repair_flag_remark = flags.get('title').strip()
                if flag_style == repair_ransom_style:
                    is_ransom_flag = True
                    ransom_flag_remark = flags.get('title').strip()
                if flag_style == pre_ransom_style:
                    pre_ransom_remark = flags.get('title').strip()
            arbitrage_percent = row.find_all('td', {'class': "cb_mov2_id"})[
                1].get_text().strip()[0:-1]  # 日内套利
            stock_price = row.find_all('td', {'class': "stock_price_id"})[
                0].string.strip()  # 股票价格
            stock_percent = row.find_all('td', {'class': "cb_mov_id"})[
                0].get_text().strip()[0:-1]  # 股票涨跌幅
            convert_stock_price = row.find_all('td', {'class': "cb_strike_id"})[
                0].get_text().strip()  # 转股价格

            premium_rate = row.find_all('td', {'class': "cb_premium_id"})[
                0].string.strip()[0:-1]  # 转股溢价率

            remain_price = row.find_all('td', {'class': "cb_price2_id"})[
                1].string.strip()  # 剩余本息
            remain_price_tax = row.find_all('td', {'class': "cb_price2_id"})[
                1]['title'].strip()[2:]  # 税后剩余本息
            is_unlist = row.get("data-unlist")  # 是否上市
            issue_date = None
            if is_unlist == 'N':
                issue_date = row.find(
                    'td', {'class': "bond_date_id"}).get_text().strip()  # 发行日期
            date_convert_distance = row.find_all('td', {'class': "cb_t_id"})[
                0].string.strip()  # 距离转股时间
            date_remain_distance = row.find_all('td', {'class': "cb_t_id"})[
                1].get_text().strip()  # 剩余到期时间 待处理异常情况
            date_remain_distance = date_remain_distance.translate(
                str.maketrans("", "", string.whitespace))
            date_return_distance = row.find_all('td', {'class': "cb_t_id"})[
                2].get_text().strip()  # 剩余回售时间 待处理异常情况
            # item['距离回售时间'].translate(str.maketrans("", "", string.whitespace))
            date_return_distance = date_return_distance.translate(
                str.maketrans("", "", string.whitespace))

            remain_amount = row.get("data-remain_amount")  # 剩余规模
            # remain_amount = row.find_all('td', {'class': "remain_amount"})[
            #     0].get_text().strip()  # 转债剩余余额
            market_cap = row.find_all('td', {'class': "market_cap"})[
                0].get_text().strip()  # 股票市值
            remain_to_cap = row.find_all('td', {'class': "cb_to_share"})[
                0].get_text().strip()[0:-1]  # 转债剩余/市值比例
            pb_el = row.find_all('td', {'class': "cb_elasticity_id"})[
                0]
            pb = pb_el.get_text().strip()  # P/B比例
            cb_to_pb = re.findall(
                r"（转股价格/每股净资产）：(.+)", pb_el['title'].strip())[0]
            # cb_to_pb = row.find_all('td', {'class': "cb_elasticity_id"})[
            #     0].get_text().strip()  # 转股价格/每股净资产

            rate_expire = row.find_all('td', {'class': "cb_BT_id"})[
                0].get_text().strip()[0:-1]  # 到期收益率
            rate_expire_aftertax = row.find_all('td', {'class': "cb_BT_id"})[
                0].get('title').strip()[6:-1]  # 税后到期收益率
            rate_return = row.find_all('td', {'class': "cb_AT_id"})[
                4].get_text().strip()[0:-1]  # 回售收益率
            old_style = row.find_all('td', {'class': "cb_wa_id"})[
                0].get_text().strip()  # 老式双底
            new_style = row.find_all('td', {'class': "cb_wa_id"})[
                1].get_text().strip()  # 新式双底
            # print("market", rate_expire, rate_return,
            #       stock_name, old_style, new_style, stock_percent, date_convert_distance, date_return_distance, date_remain_distance)
            # fund_df = pd.DataFrame({'id': id_list, 'fund_code': code_list, 'morning_star_code': morning_star_code_list, 'fund_name': name_list, 'fund_cat': fund_cat,
            #                         'fund_rating_3': fund_rating_3, 'fund_rating_5': fund_rating_5, 'rate_of_return': rate_of_return})
            item_stock = code_stdevry_map.get(stock_code)
            item = {
                'cb_code': cb_code,
                'cb_name': cb_name,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'industry': item_stock.get('industry') if item_stock else '-',
                'price': float(price),
                'premium_rate': float(premium_rate),
                'stock_stdevry': item_stock.get('stdevry') if item_stock else '-',
                'cb_to_pb': float(cb_to_pb),
                'date_remain_distance': date_remain_distance,
                'date_return_distance': date_return_distance,
                # 快到期或者强赎的情况为<-100
                'rate_expire': -100 if '<-100' in rate_expire else (100 if ('>100' in rate_expire) else float(rate_expire)),
                'rate_expire_aftertax': -100 if '<-100' in rate_expire_aftertax else (100 if ('>100' in rate_expire_aftertax) else float(rate_expire_aftertax)),
                'remain_to_cap': float(remain_to_cap),
                'is_repair_flag': str(is_repair_flag),
                'repair_flag_remark': repair_flag_remark,
                'pre_ransom_remark': pre_ransom_remark,
                'is_ransom_flag': str(is_ransom_flag),
                'ransom_flag_remark': ransom_flag_remark,

                'remain_amount': float(remain_amount),
                'market_cap': int(market_cap.replace(",", "")),

                'last_price': None,
                'last_cb_percent':  None,
                'cb_percent': float(cb_percent),
                'stock_price': float(stock_price),
                'stock_percent': float(stock_percent),
                'last_stock_price': None,
                'last_stock_percent': None,
                'arbitrage_percent': float(arbitrage_percent),
                'convert_stock_price': float(convert_stock_price),
                'pb': float(pb),
                'market': market,

                'remain_price': float(remain_price),
                'remain_price_tax': float(remain_price_tax),

                'is_unlist': is_unlist,
                'last_is_unlist': is_unlist if is_start else "Y",
                'issue_date': date if issue_date == '今日上市' else issue_date,
                'date_convert_distance': date_convert_distance,

                'rate_return': rate_return,

                'old_style': float(old_style.replace(",", "")),
                'new_style': float(new_style.replace(",", "")),
                'rating': rating,
                'id': worker.get_id(),
                'cb_id': cb_id,
            }
            last_record = last_map.get(cb_code)
            if last_record:
                item['last_price'] = last_record.get(rename_map.get('price'))
                item['last_stock_price'] = last_record.get(
                    rename_map.get('stock_price'))
                item['last_stock_percent'] = round((float(stock_price) - last_record.get(
                    rename_map.get('stock_price')))/last_record.get(rename_map.get('stock_price'))*100, 2)
                item['last_cb_percent'] = round((float(price) - last_record.get(
                    rename_map.get('price')))/last_record.get(rename_map.get('price'))*100, 2)
                item['last_is_unlist'] = last_record.get(
                    rename_map.get("is_unlist"))
            if is_output and not is_save_database:
                del item['id']
                del item['cb_id']
            if is_save_database:
                delete_key_for_store(item)
            list.append(item)
        except Exception:
            raise (Exception)

    df = pd.DataFrame.from_records(list)
    # 输出到excel
    if is_output:
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
            output_excel(filter_data, sheet_name=strategy_name, date=date)
            filter_data_dict[filter_key] = filter_data
        if is_start:
            print('success!!! data total: ', len(list))
            return
        all_df_rename = df.rename(columns=rename_map).reset_index()
        percents = []
        for strategy in strategy_list:
            strategy_name = strategy['name']
            head_count = strategy['head_count']
            all_strategy_df = xls.parse(strategy['name'])
            all_strategy_df['可转债代码'] = all_strategy_df['可转债代码'].astype(str)
            strategy_df = all_strategy_df.head(
                head_count)  # 读取前20条
            print(f"{strategy_name}'s len", len(strategy_df))
            cur_percent = 0
            cur_stocks_percent = 0
            if len(strategy_df) > 0:
                strategy_df = pd.merge(all_df_rename, strategy_df,
                                       on=['可转债代码'], how='inner')
                cur_percent = round(strategy_df["较上期涨跌幅_x"].mean().round(
                    2) * (len(strategy_df) / head_count), 2)  # 乘以仓位
                cur_stocks_percent = round(strategy_df["较上期股价涨跌幅_x"].mean().round(
                    2) * (len(strategy_df) / head_count), 2)
            strategy['percent'] = cur_percent
            strategy['stocks_percent'] = cur_stocks_percent

            percents.append({
                'name': f'{strategy_name}(距{compare_date})',
                'total': len(all_strategy_df),
                'head': len(strategy_df),
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
        # last_accumulate_item = dict()
        # for percent in last_period_percents:
        #     if percent['name'] == '累计涨跌幅(all)':
        #         last_accumulate_item = percent
        # last_accumulate = last_accumulate_item.get(
        #     'percent') if last_accumulate_item.get('percent') else 0
        # percents.append({
        #     'name': '累计涨跌幅(all)',
        #     'percent': round(((last_accumulate / 100 + 1) * (1 + all_percent / 100) - 1) * 100, 2),
        # })
        stats_data[date] = percents
        write_fund_json_data(stats_data, filename, file_dir)
        output_excel(pd.DataFrame(percents), sheet_name="汇总", date=date)
    if is_save_database:
        # 入库
        store_database(df)
    print('success!!! data total: ', len(list))


def backtest():
    htmlFiles = os.listdir('./html/')
    dateList = []
    for file in htmlFiles:
        dateList.append(file[0:10])

    sorted_dates = sorted(dateList)
    prev_date = None
    for idx, date in enumerate(sorted_dates):
        cur_date = date
        compare_date = prev_date if prev_date else sorted_dates[
            0] if idx == 0 else sorted_dates[idx-1]
        print(idx, cur_date, compare_date)
        # last_path = f'{out_dir}{compare_date}_cb_list.xlsx'
        # if idx != 0 and not os.path.exists(last_path):

        #     continue
        is_save_database = False
        is_output = True
        impl(is_output, is_save_database, date=cur_date,
             compare_date=compare_date)
        prev_date = cur_date  # 成功输出之后，更新prev_date


if __name__ == "__main__":
    input_value = input("请输入下列序号执行操作:\n \
            1.“输出到本地” \n \
            2.“存到数据库” \n \
            3.“回测” \n \
            4.“可视化” \n \
            5.“多因子策略回测” \n \
        输入：")
    date = datetime.now().strftime("%Y-%m-%d")
    # date = "2023-04-21"
    compare_date = "2023-05-06"
    if input_value == '1':
        is_save_database = False
        is_output = True
        impl(is_output, is_save_database, date=date,
             compare_date=compare_date)
    elif input_value == '2':
        is_save_database = True
        is_output = False
        impl(is_output, is_save_database, date=date,
             compare_date=compare_date)
    elif input_value == '3':
        backtest()
        plot()
    elif input_value == '4':
        plot()
    elif input_value == '5':
        # file_dir = 'bond=0.7_stock=0.3_price=115_count=10_premium=25_premium_ratio=0.3_stdevry=30_max_price=130/'
        file_dir = 'out/'
        parent_dir = './'
        impl_multiple_factors(file_dir=file_dir, parent_dir=parent_dir)
