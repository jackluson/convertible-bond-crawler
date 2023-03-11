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
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from lib.mysnowflake import IdWorker
from utils.connect import connect
from utils.excel import update_xlsx_file
from utils.login import login

connect_instance = connect()
connect = connect_instance.get('connect')
cursor = connect_instance.get('cursor')

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

    'cb_percent': '转债涨跌幅',
    'stock_price': '股价',
    'stock_percent': '股价涨跌幅',
    'arbitrage_percent': '日内套利',
    'convert_stock_price': '转股价格',
    'pb': '市净率',
    'market': '市场',

    'remain_price': '剩余本息',
    'remain_price_tax': '税后剩余本息',

    'is_unlist': '是否上市',
    'issue_date': '发行日期',
    'date_convert_distance': '距离转股时间',

    'remain_amount': '剩余规模',
    'market_cap': '股票市值',


    'rate_return': '回售收益率',

    'old_style': '老式双底',
    'new_style': '新式双底',
    'rating': '债券评级',
    'id': 'id',
    'cb_id': 'id',
}


def get_bs_source(is_read_local=False):
    # 利用BeautifulSoup解析网页源代码
    date = datetime.now().strftime("%Y-%m-%d")
    path = './html/' + date + "_output.html"

    bs = None
    if is_read_local:
        htmlfile = open(path, 'r', encoding='utf-8')
        bs = BeautifulSoup(htmlfile.read(), 'lxml')
        htmlfile.close()
    else:
        with open(path, "w", encoding='utf-8') as file:
            page_url = "https://www.ninwin.cn/index.php?m=cb&a=cb_all"
            chrome_driver = login(page_url, is_cookies_login=True)
            time.sleep(5)
            data = chrome_driver.page_source
            table = chrome_driver.find_element(By.ID, 'cb_hq')
            # tbody = table.get_attribute('innerHTML')
            tbody = table.find_element(
                By.XPATH, 'tbody').get_attribute('innerHTML')
            # row = table.find_elements_by_xpath('tbody/tr')

            bs = BeautifulSoup(tbody, 'lxml')
            # prettify the soup object and convert it into a string
            # file.write(data)
            file.write(str(bs.prettify()))
    return bs


def output_excel(df, *, sheet_name="All"):
    date = datetime.now().strftime("%Y-%m-%d")
    path = './out/' + date + '_cb_list.xlsx'
    df_output = df.rename(columns=rename_map).reset_index(drop=True)
    update_xlsx_file(path, df_output, sheet_name)
    # df.to_excel(path, index=False)


def store_database(df):
    sql_insert = generate_insert_sql(
        rename_map, 'convertible_bond', ['id', 'cb_code'])
    list = df.values.tolist()
    print("sql_insert", sql_insert)
    cursor.executemany(sql_insert, list)
    connect.commit()


def generate_insert_sql(target_dict, table_name, ignore_list):
    keys = ','.join(target_dict.keys())
    values = ','.join(['%s'] * len(target_dict))
    update_values = ''
    for key in target_dict.keys():
        if key in ignore_list:
            continue
        update_values = update_values + '{0}=VALUES({0}),'.format(key)

    sql_insert = "INSERT INTO {table} ({keys}) VALUES ({values})  ON DUPLICATE KEY UPDATE {update_values}; ".format(
        table=table_name,
        keys=keys,
        values=values,
        update_values=update_values[0:-1]
    )
    return sql_insert


repair_flag_style = 'color:blue'
repair_ransom_style = 'color:red'


def main(is_output, is_save_database):
    isReadLocal = False
    date = datetime.now().strftime("%Y-%m-%d")
    output_path = './html/' + date + "_output.html"
    if os.path.exists(output_path):
        if os.path.getsize(output_path) > 0:
            isReadLocal = True
    bs = get_bs_source(isReadLocal)
    # print(bs)
    rows = bs.find_all('tr')
    print("rows", len(rows))
    list = []
    worker = IdWorker()
    dt = datetime.now()
    for index in range(0, len(rows)):
        row = rows[index]
        try:
            # print(row)
            cb_id = row.get("data-id")  # 获取属性值
            cb_name = row.get("data-cb_name")
            cb_code = row.get("data-cbcode")
            stock_code = row.get("data-stock_code")[2:]
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
            for flags in cb_flags:
                if flags.get('style') == repair_flag_style:
                    is_repair_flag = True
                    repair_flag_remark = flags.get('title').strip()
                if flags.get('style') == repair_ransom_style:
                    is_ransom_flag = True
                    ransom_flag_remark = flags.get('title').strip()
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
            #item['距离回售时间'].translate(str.maketrans("", "", string.whitespace))
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
            item = {
                'cb_code': cb_code,
                'cb_name': cb_name,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'price': float(price),
                'premium_rate': float(premium_rate),
                'cb_to_pb': float(cb_to_pb),
                'date_remain_distance': date_remain_distance,
                'date_return_distance': date_return_distance,
                # 快到期或者强赎的情况为<-100
                'rate_expire': -100 if '<-100' in rate_expire else float(rate_expire),
                'rate_expire_aftertax': -100 if '<-100' in rate_expire_aftertax else float(rate_expire_aftertax),
                'remain_to_cap': float(remain_to_cap),
                'is_repair_flag': str(is_repair_flag),
                'repair_flag_remark': repair_flag_remark,
                'is_ransom_flag': str(is_ransom_flag),
                'ransom_flag_remark': ransom_flag_remark,

                'cb_percent': float(cb_percent),
                'stock_price': float(stock_price),
                'stock_percent': float(stock_percent),
                'arbitrage_percent': float(arbitrage_percent),
                'convert_stock_price': float(convert_stock_price),
                'pb': float(pb),
                'market': market,

                'remain_price': float(remain_price),
                'remain_price_tax': float(remain_price_tax),

                'is_unlist': is_unlist,
                'issue_date': dt.strftime('%y-%m-%d') if issue_date == '今日上市' else issue_date,
                'date_convert_distance': date_convert_distance,

                'remain_amount': float(remain_amount),
                'market_cap': int(market_cap.replace(",", "")),

                'rate_return': rate_return,

                'old_style': float(old_style.replace(",", "")),
                'new_style': float(new_style.replace(",", "")),
                'rating': rating,
                'id': worker.get_id(),
                'cb_id': cb_id,
            }
            if is_output and not is_save_database:
                del item['id']
                del item['cb_id']
            list.append(item)
        except Exception:
            print(row)
            raise Exception

    df = pd.DataFrame.from_records(list)
    print(df)
    # 输出到excel
    if is_output:
        output_excel(df, sheet_name='All')
        filter_profit_due(df)
        filter_return_lucky(df)
        filter_double_low(df)
    if is_save_database:
        # 入库
        store_database(df)
    print('success!!! data total: ', len(list))
    # time.sleep(3600)

# df[df["A"].str.contains("Hello|Britain")]


def filter_profit_due(df):
    df_filter = df.loc[(df['rate_expire_aftertax'] > 0)
                       #    & (df['price'] < 115)
                       & (df['date_convert_distance'] == '已到')
                       & (df['cb_to_pb'] > 1.5)
                       & (df['is_repair_flag'] == 'True')
                       & (df['remain_to_cap'] > 5)
                       ]

    def my_filter(row):
        if '暂不行使下修权利' in row.repair_flag_remark or '距离不下修承诺' in row.repair_flag_remark:
            return False
        return True
    df_filter = df_filter[df_filter.apply(my_filter, axis=1)]
    output_excel(df_filter, sheet_name="到期保本")


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
    output_excel(df_filter, sheet_name="回售摸彩")


def filter_double_low(df):
    df_filter = df.loc[(df['date_convert_distance'] == '已到')
                       & (df['date_return_distance'] != '无权')
                       & (~df["cb_name"].str.contains("EB"))
                       #    & (df['date_return_distance'] != '回售内')
                       & (df['is_ransom_flag'] == 'False')
                       & (df['cb_to_pb'] > 0.5)
                       #    & (df['remain_to_cap'] > 5)
                       & (((df['price'] < 128)
                           & (df['premium_rate'] < 10)) | ((df['price'] < 120)
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
    output_excel(df_filter, sheet_name="低价格低溢价")


if __name__ == "__main__":
    input_value = input("请输入下列序号执行操作:\n \
        1.“输出到本地” \n \
        2.“输出到MySQL” \n \
    输入：")
    if input_value == '1':
        is_save_database = False
        is_output = True
        main(is_output, is_save_database)
    elif input_value == '2':
        is_save_database = True
        is_output = False
        main(is_output, is_save_database)
