'''
Desc:
File: /store.py
File Created: Saturday, 15th July 2023 6:05:40 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
from datetime import datetime
from lib.mysnowflake import IdWorker
import pandas as pd
from config import out_dir, rename_map, save_database_map, summary_filename
from utils.index import generate_insert_sql
from utils.connect import new_connect
from modules.source import crawler


del_keys = []


def delete_key_for_store(data):
    del data['industry']
    del data['classi_name']
    del data['provincial_name']
    del data['main_operation_business']
    del data['pb_percent']
    del data['pe']
    del data['pe_percent']
    del data['pe_koufei']
    del data['pe_koufei_percent']

    del data['last_price']
    del data['last_cb_percent']
    del data['last_stock_price']
    del data['last_stock_percent']
    del data['last_is_unlist']
    del data['turnover_rate']
    del data['stock_stdevry']
    if data.get('weight_score'):
        del data['weight_score']
    return data


def store_database(date=None):
    if date == None:
        date = datetime.now().strftime("%Y-%m-%d")
        date = "2023-07-14"
    worker = IdWorker()
    data_list = crawler(date=date)
    new_list = []
    for index in range(len(data_list)):
        item = data_list[index]
        del item['turnover_rate']
        new_list.append({
            'id': worker.get_id(),
            **item,
        })
    df = pd.DataFrame.from_records(new_list)
    # 入库
    sql_insert = generate_insert_sql(
        save_database_map, 'convertible_bond', ['id', 'cb_code'])
    list = df.values.tolist()
    connect_instance = new_connect()
    connect = connect_instance.get('connect')
    cursor = connect_instance.get('cursor')
    cursor.executemany(sql_insert, list)
    connect.commit()


if __name__ == "__main__":
    store_database()
