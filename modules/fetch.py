'''
Desc:
File: /fetch.py
File Created: Thursday, 10th August 2023 11:02:31 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''

from infra.api.jisilu import ApiJiSiLu
from infra.api.snowball import ApiSnowBall


def fetch_indictor():
    api = ApiJiSiLu()
    data = api.get_last_indicator()
    return data


def modify_portfolio(symbols, pnames):
    api = ApiSnowBall(need_login=True)
    resp = api.cancel_portfolio(symbols)
    print("resp", resp)
    # res = api.modify_portfolio(symbols, pnames)
    # print("res", res)


if __name__ == "__main__":
    symbols = "SH111012"
    pnames = "focus"
    modify_portfolio(symbols, pnames)
