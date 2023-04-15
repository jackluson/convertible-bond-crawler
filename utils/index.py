'''
Desc:
File: /index.py
File Created: Sunday, 9th April 2023 1:06:58 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import os
import json
from bs4 import BeautifulSoup
import time
from .login import login
from .connect import connect
from .excel import update_xlsx_file
from selenium.webdriver.common.by import By
from config import rename_map, out_dir, summary_filename
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors

connect_instance = connect()
connect = connect_instance.get('connect')
cursor = connect_instance.get('cursor')


def get_bs_source(date, is_read_local=False):

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


def delete_key_for_store(data):
    del data['last_price']
    del data['last_cb_percent']
    del data['last_stock_price']
    del data['last_stock_percent']
    del data['last_is_unlist']
    del data['industry']
    del data['stock_stdevry']
    del data['pre_ransom_remark']
    if data.get('weight_score'):
        del data['weight_score']
    return data


def store_database(df):
    store_map = delete_key_for_store(rename_map)
    sql_insert = generate_insert_sql(
        store_map, 'convertible_bond', ['id', 'cb_code'])
    list = df.values.tolist()
    cursor.executemany(sql_insert, list)
    connect.commit()


def output_excel(df, *, sheet_name="All", date):
    path = f'{date}_cb_list.xlsx'
    file_dir = f'{out_dir}'
    path = file_dir + path
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
        print("目录新建成功：%s" % file_dir)
    df_output = df.rename(columns=rename_map).reset_index(drop=True)
    update_xlsx_file(path, df_output, sheet_name)
    # df.to_excel(path, index=False)


def plot():
    filename = summary_filename
    file_dir = f'{out_dir}'
    percents = []
    # %matplotlib inline
    with open(file_dir + filename) as json_file:
        stats_data = json.load(json_file)
        for date in stats_data:
            row_data = {
                'date': date
            }
            for item in stats_data[date]:
                name = item['name'][0: -13]
                if '累计' in name:
                    continue
                stocks_name = f'{name}_stocks'
                row_data[name] = item['percent'] / 100 + 1
                row_data[stocks_name] = item['stocks_percent'] / 100 + 1
            percents.append(row_data)
    df_percents = pd.DataFrame(percents).set_index('date')
    # df_percents = df3.cumsum()
    # %matplotlib inline
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    df_percents.cumprod().round(4).plot(
        grid=True, figsize=(15, 7), title=file_dir[10:-1])
    mplcursors.cursor(hover=True)
    plt.show()
