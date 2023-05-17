'''
Desc:
File: /multiple_factors.py
File Created: Sunday, 16th April 2023 12:59:47 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
import logging
import os
import pandas as pd
from config import rename_map
from datetime import datetime
import matplotlib.pyplot as plt
import mplcursors


def get_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file, 'w')
    formatter = logging.Formatter(
        '[line:%(lineno)d] - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


class MultipleFactorsStrategy():
    max_hold_num = 12
    holdlist = []
    # count_position = 20
    per = 0.083
    dates = []
    cur_date = None
    data_source_dir = ''
    date_map_source = dict()
    earn_percent = 1
    record_percents = []
    date_percent = 0
    sell_win_count = 0
    sell_loss_count = 0
    until_win = False
    # sell_percents = []
    # sell_percent = 0

    def __init__(self, *, file_dir, parent_dir='./backlog/', until_win=False):
        # log_file_name = 'log/' + begin_date + '至' + end_date + '_momentum.log'
        # self.logger = get_logger(log_file_name, log_file_name)
        self.until_win = until_win
        self.data_source_dir = f'{parent_dir}{file_dir}'
        suffix = '_win' if self.until_win else ''
        log_file_name = f'./backlog/log/multiple_factors_{file_dir[0:-1]}{suffix}.log'
        self.logger = get_logger(log_file_name, log_file_name)
        self.make_data_source()

    def make_data_source(self):
        files = os.listdir(self.data_source_dir)
        dateList = []
        code_field_key = rename_map['cb_code']
        for file in files:
            if not file.endswith('.xlsx'):
                continue
            date = file[0:10]
            dateList.append(date)
            last_path = f'{self.data_source_dir}{file}'
            xls = pd.ExcelFile(last_path, engine='openpyxl')
            # parse all
            df_all = xls.parse("All_ROW")
            df_all[code_field_key] = df_all[code_field_key].astype(str)
            df_all['code'] = df_all[code_field_key]
            df_all = df_all.set_index(['code'])
            # parse candidate
            df_candidate = xls.parse('多因子')
            df_candidate[code_field_key] = df_candidate[code_field_key].astype(
                str)
            df_candidate['code'] = df_candidate[code_field_key]
            df_candidate = df_candidate.set_index(['code'])
            self.date_map_source[date] = {
                'all': df_all,
                'candidate': df_candidate
            }
            # if len(dateList) > 2:
            #     break

        self.dates = sorted(dateList)

    def traverse(self):
        for index in range(0, len(self.dates)):
            self.trade(index)

    def trade(self, index):
        self.cur_date = self.dates[index]
        code_field_key = rename_map['cb_code']
        date_data = self.date_map_source[self.cur_date]
        candidate = date_data['candidate']

        if index == 0:
            for index, item in candidate.head(self.max_hold_num).iterrows():
                self.buyone(item)
        else:
            self.pre_date = self.dates[index - 1]
            sell_list = []
            buy_list = []
            keep_list = []
            # make sell holdlist
            for item in self.holdlist:
                item_code = item.get('code')
                latest_item = date_data['all'].loc[item_code]
                cur_price = latest_item['转债价格']
                buy_price = item['buy_price']
                if latest_item['是否满足强赎条件']:
                    sell_list.append(item)
                    continue
                if cur_price <= buy_price and self.until_win:
                    keep_list.append(item)
                    continue
                is_exist = False
                for index, candidate_item in candidate.iterrows():
                    if candidate_item[code_field_key] == item_code:
                        is_exist = True
                        break
                if is_exist == False:
                    sell_list.append(item)
                else:
                    keep_list.append(item)
            keep_cnt = len(keep_list)
            # make buy holdlist
            for index, candidate_item in candidate.iterrows():
                if len(buy_list) + keep_cnt == self.max_hold_num:
                    break
                cur_price = latest_item['转债价格']
                candidate_item_code = candidate_item[code_field_key]
                is_exist = False
                for item in self.holdlist:
                    if candidate_item_code == item.get('code'):
                        is_exist = True
                        break
                if is_exist == False:
                    buy_list.append(candidate_item)
            self.compute()
            for item in sell_list:
                self.sellone(item)
            for item in buy_list:
                self.buyone(item)
            self.logger.warn(
                f"[汇总] -- 时间:{self.cur_date},最新持仓数量:{len(self.holdlist)}, 留仓数量:{keep_cnt}, 卖出数量:{len(sell_list)},买入数量:{len(buy_list)}")

    def buyone(self, item):
        hold_item = {
            'name': item['可转债名称'],
            'code': item['可转债代码'],
            'buy_price': item['转债价格'],
            'buy_date': self.cur_date,
            'last_price': item['转债价格'],
            'ratio': self.per,
        }
        self.holdlist.append(hold_item)
        self.logger.info("[buy] -- 买入时间:%s, name:%s, code:%s, 买入价格:%f," % (
            hold_item['buy_date'], hold_item['name'], hold_item['code'], hold_item['buy_price'],))

    def sellone(self, item):
        date_data = self.date_map_source[self.cur_date]
        latest_item = date_data['all'].loc[item['code']]
        sell_item = {
            **item,
            'sell_price': latest_item['转债价格'],
            'sell_date': self.cur_date,
        }
        for i in range(len(self.holdlist)):
            if self.holdlist[i]['code'] == sell_item['code']:
                del self.holdlist[i]
                break
        percent = round(
            (sell_item['sell_price'] - sell_item['buy_price']) / sell_item['buy_price'] * 100, 2)
        if percent > 0:
            self.sell_win_count = self.sell_win_count + 1
        else:
            self.sell_loss_count = self.sell_loss_count + 1

        date_format = '%Y-%m-%d'  # 日期格式
        sell_date = datetime.strptime(sell_item['sell_date'], date_format)
        buy_date = datetime.strptime(sell_item['buy_date'], date_format)
        hold_days = (sell_date - buy_date).days
        self.logger.info(
            f"[sell] -- 卖出时间:{sell_item['sell_date']}, name:{sell_item['name']}, code:{sell_item['code']}, 买出价格:{sell_item['sell_price']}, 买入价格:{sell_item['buy_price']}, 盈亏比例:{percent}%, 买入时间:{sell_item['buy_date']}, 持有天数:{hold_days}")

    def compute(self):
        self.date_percent = 0
        for item in self.holdlist:
            self.compute_one(item)
        self.record_percents.append({
            'date': self.cur_date,
            'percent': self.date_percent,
        })
        self.logger.warn(
            f"[汇总] -- 时间:{self.cur_date}, percent:{round(self.date_percent * 100, 2)}%, 当前持仓数量:{len(self.holdlist)}")

    def compute_one(self, item):
        date_data = self.date_map_source[self.cur_date]
        latest_item = date_data['all'].loc[item['code']]
        cur_price = latest_item['转债价格']
        last_price = item['last_price']
        percent = (cur_price - last_price) / last_price

        self.date_percent = round(
            self.date_percent + percent * item['ratio'], 4)
        for i in range(len(self.holdlist)):
            if self.holdlist[i]['code'] == item['code']:
                self.holdlist[i] = {
                    **self.holdlist[i],
                    'last_price': latest_item['转债价格'],
                }
                break

    def summary(self):
        trade_count = self.sell_win_count + self.sell_loss_count
        self.logger.warn(
            f"[汇总] -- 卖出胜数:{self.sell_win_count}, 卖出输次:{self.sell_loss_count}, 卖出总次数:{trade_count}, 胜率:{round(self.sell_win_count / trade_count * 100, 2)}%")
        plt_data = pd.DataFrame.from_records(
            self.record_percents)
        plt_data = plt_data.set_index(['date'])
        plt_data['percent'] = plt_data['percent'] + 1
        df_cumprod = plt_data.cumprod().round(4)
        df_cumprod.plot(grid=True, figsize=(15, 7))
        mplcursors.cursor(hover=True)
        df_cumprod['max_percent'] = df_cumprod['percent'].rolling(
            len(df_cumprod), min_periods=1).max()
        df_cumprod['dd'] = (df_cumprod['percent'] -
                            df_cumprod['max_percent']).round(4)

        df_cumprod['max_dd'] = df_cumprod['dd'].rolling(
            len(df_cumprod), min_periods=1).min().round(4)
        print(df_cumprod)
        total_percent = round(
            (df_cumprod.iloc[-1]['percent'] - 1) * 100, 2)  # 总盈亏比例
        max_percent = round(
            (df_cumprod.iloc[-1]['max_percent'] - 1) * 100, 2)  # 最大盈亏比例
        max_dd = round(df_cumprod.iloc[-1]['max_dd'] * 100, 2)  # 最大回撤
        self.logger.warn(
            f"[汇总] - - 当前盈亏: {total_percent} %, 最大盈亏: {max_percent}%, 最大回撤: {max_dd}%"
        )
        # print(plt_data.cumprod().round(4))
        plt.show()
        pass


def impl_multiple_factors(*, file_dir, parent_dir='./backlog/', until_win=False):
    strategy = MultipleFactorsStrategy(
        file_dir=file_dir, parent_dir=parent_dir, until_win=until_win)
    strategy.traverse()
    strategy.summary()


if __name__ == "__main__":
    impl_multiple_factors()
