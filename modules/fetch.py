'''
Desc:
File: /fetch.py
File Created: Thursday, 10th August 2023 11:02:31 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''

from infra.api.jisilu import ApiJiSiLu


def fetch_indictor():
    api = ApiJiSiLu()
    data = api.get_last_indicator()
    return data
