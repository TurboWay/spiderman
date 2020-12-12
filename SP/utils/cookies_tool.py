#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/7/16 14:54
# @Author : way
# @Site : all
# @Describe: 操作 cookies 工具

def get_normal_cookies(cookies_url, source=False):
    """
    :param cookies_url: 一般请求获取cookies
    :param source: 默认False
                   True 返回 cookies, response
                   False 返回 cookies
    :return: dict
    """
    import requests
    headers = {
        'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/69.0.3497.100Safari/537.36'
    }
    response = requests.get(cookies_url, headers)
    cookies = requests.utils.dict_from_cookiejar(response.cookies)
    if source:
        return cookies, response
    return cookies


def get_sp_cookies(cookies_url, times=2, source=False):
    """
    :param cookies_url: 特殊请求, 比如等待js 获取cookies
    :param times: 等待时长
    :param source: 默认False
                   True 返回 cookies, page_source
                   False 返回 cookies
    :return: dict
    """
    import requests, json
    from SP.settings import SPLASH_URL

    lua_script = f'''
    function main(splash)
        splash:go("{cookies_url}")
        splash:wait({times})
        local html = splash:html()
        local cookies = splash:get_cookies()
        return {{html=html, cookies=cookies}}
    end
    '''
    headers = {'content-type': 'application/json'}
    data = json.dumps({'lua_source': lua_script})
    response = requests.post(SPLASH_URL + '/execute', headers=headers, data=data).json()
    cookies = {}
    for cookie in response['cookies']:
        cookies.update(cookie)
    if source:
        return cookies, response['html']
    return cookies


def dict_from_cookies_str(cookies_str):
    """
    :param cookies_str: cookies字符串
    :return: dict
    """
    return dict([i.split('=', 1) for i in cookies_str.split(';')])


def get_ys_cookies(ys_url, source=False):
    """
        :param cookies_url: 云锁网站网址,获取cookies
        :param source: 默认False
                   True 返回 cookies, page_source
                   False 返回 cookies
        :return:dict
    """
    import requests
    headers = {
        'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/69.0.3497.100Safari/537.36'
    }
    resp = requests.get(ys_url, timeout=60)
    cookie = {}
    for key, value in resp.cookies.items():
        cookie[key] = value

    resp = requests.get(
        '{}{}'.format(ys_url, '?security_verify_data=313932302c31303830'),
        cookies=cookie,
        timeout=60
    )
    for key, value in resp.cookies.items():
        cookie[key] = value
    if source:
        resp = requests.get(
            url=ys_url,
            cookies=cookie,
            headers=headers,
            timeout=60
        )
        return cookie, resp
    return cookie
