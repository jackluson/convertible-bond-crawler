'''
Desc:
File: /crawler.py
File Created: Saturday, 15th July 2023 11:26:47 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''

import os
import string
import re
from utils.index import get_bs_source
from config import repair_flag_style, repair_ransom_style, pre_ransom_style, rename_map, strategy_list, out_dir, summary_filename, real_mid_temperature_map


def crawler(*, date):
    output_path = './html/' + date + "_output.html"
    if os.path.exists(output_path):
        if os.path.getsize(output_path) > 0:
            isReadLocal = True
    bs = get_bs_source(date, isReadLocal)
    rows = bs.find_all('tr')
    list = []
    for index in range(0, len(rows)):
        row = rows[index]
        try:
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
            trade_amount = row.find_all('td', {'class': "cb_trade_amount_id"})[
                0].get_text().strip().replace(',', '')   # 成交额（单位是百万）
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
                'cb_id': cb_id,
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
                'rate_expire': -100 if '<-100' in rate_expire else (100 if ('>100' in rate_expire) else float(rate_expire)),
                'rate_expire_aftertax': -100 if '<-100' in rate_expire_aftertax else (100 if ('>100' in rate_expire_aftertax) else float(rate_expire_aftertax)),
                'remain_to_cap': float(remain_to_cap),
                'is_repair_flag': str(is_repair_flag),
                'repair_flag_remark': repair_flag_remark,
                'pre_ransom_remark': pre_ransom_remark,
                'is_ransom_flag': str(is_ransom_flag),
                'ransom_flag_remark': ransom_flag_remark,

                'remain_amount': round(float(remain_amount), 2),
                'trade_amount': float(trade_amount) / 100,  # 转换单位亿
                # 转换单位亿
                # 换手率
                'turnover_rate': round(float(trade_amount) / float(remain_amount), 2),
                'market_cap': int(market_cap.replace(",", "")),

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
                'issue_date': date if issue_date == '今日上市' else issue_date,
                'date_convert_distance': date_convert_distance,

                'rate_return': rate_return,

                'old_style': float(old_style.replace(",", "")),
                'new_style': float(new_style.replace(",", "")),
                'rating': rating,
            }
            list.append(item)
        except Exception:
            raise (Exception)
    return list
