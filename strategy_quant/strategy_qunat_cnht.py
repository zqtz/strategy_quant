import time
import requests
import json
import datetime
from selenium.webdriver import Chrome
import urllib.request
import re
import base64
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

# 设置无头浏览器
options = Options()
options.add_argument('--headless')
from selenium.webdriver.common.by import By

# 设置验证码识别
def code_verify():
    host = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=oa6VVGS7ldI5GG1e3fHrgvB6&client_secret=xdaZFWKnqt2Hsxvnpd2GDo2QNpfGrHLQ&"
    response = requests.get(host)
    if response:
        access_token = re.findall(r'"access_token":"(.*?)"', response.text)[0]
    '''
    通用文字识别（高精度版）
    '''
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    # 二进制方式打开图片文件
    f = open('cnht.jpg', 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img}
    access_token = access_token
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        verify_code = response.json()['words_result'][0]['words']
        print(verify_code)
        return verify_code

# 登录并获取cookies
def login_get_cookies():
    web = Chrome(options=options)
    web.get('https://hw.cnht.com.cn/')
    web.find_element(By.XPATH,'//*[@id="account_content"]').send_keys('输入你的证券账号')
    web.find_element(By.XPATH,'//*[@id="password"]').send_keys('输入你的密码')
    png = web.find_element(By.XPATH,'//*[@id="kaptchaImage"]').screenshot_as_png
    with open('cnht.jpg','wb')as f:
        f.write(png)
    verify_code = code_verify()
    web.find_element(By.XPATH,'//*[@id="kaptcapCode"]').send_keys(verify_code)
    web.find_element(By.XPATH,'//*[@id="loginButtion"]').click()
    cookies = web.get_cookies()[0]['value']
    return cookies

# 获取证券前价格
def get_current_price(stock_url):
    resp = requests.get(stock_url)
    if resp.status_code == 200:
        return resp.text.split(',')[3]
    return None

# 定义买入函数
def buy(buy_url,stock_url):
    data = {
        'stock_code':'511880',
        'entrust_price':float(get_current_price(stock_url))+0.001,
        'entrust_amount':'100',
        'entrust_prop':'0',
        'entrust_bs':'1',
        'stock_account':'输入你的对应股票市场的股东账号',
        'exchange_type':'1',
    }
    headers = {
        'accept':'application/json, text/javascript, */*; q=0.01',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
        'cache-control':'no-cache',
        'content-length':'123',
        'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie':'fund_account=securities_account_number; JSESSIONID='+str(login_get_cookies()),
        'origin':'https://hw.cnht.com.cn',
        'pragma':'no-cache',
        'referer':'https://hw.cnht.com.cn/trade/buy.html',
        'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-origin',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'x-requested-with':'XMLHttpRequest',
    }
    resp = requests.post(buy_url, headers=headers, data=data).json()
    print(resp['data'])

# 定义卖出函数
def sell_yhrl(sell_url,stock_url):
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'content-length': '127',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'fund_account=securities_account_number; JSESSIONID='+str(login_get_cookies()),
        'origin': 'https://hw.cnht.com.cn',
        'pragma': 'no-cache',
        'referer': 'https://hw.cnht.com.cn/trade/sell.html',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'stock_code': '511880',
        'entrust_price': get_current_price(stock_url),
        'entrust_amount': '100',
        'entrust_prop': '0',
        'entrust_bs': '2',
        'stock_account': '输入你的对应股票市场的股东账号',
        'exchange_type': '1',
    }
    resp = requests.post(sell_url,headers=headers,data=data)
    print(resp['data'])

# 定义卖出函数
def sell_nhg(nhg_sell_url,nhg_url):
    cookie = 'fund_account=securities_account_number; JSESSIONID='+str(login_get_cookies())
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'content-length': '124',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': cookie,
        'origin': 'https://hw.cnht.com.cn',
        'pragma': 'no-cache',
        'referer': 'https://hw.cnht.com.cn/trade/sell.html',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'stock_code': '131810',
        'entrust_price': get_current_price(nhg_url),
        'entrust_amount': '100',
        'entrust_prop': '0',
        'entrust_bs': '2',
        'stock_account': '输入你的对应股票市场的股东账号',
        'exchange_type': '2',
    }
    resp = requests.post(nhg_sell_url,data=data,headers=headers)
    print(resp.json()['data'])

# 定义一个投资策略
def strategy():
    stock_url = 'http://hq.sinajs.cn/?format=text&list=sh511880'#获取证券价格的api网页接口
    by_url = 'https://hw.cnht.com.cn/trade/stock/buy/511880?random=0.42892111184764237'
    sell_url = 'https://hw.cnht.com.cn/trade/stock/sell/511880?random=0.5302265971135136'
    nhg_url = 'https://hq.sinajs.cn/?format=text&list=sz131810'
    nhg_sell_url = 'https://hw.cnht.com.cn/trade/stock/sell/131810?random=0.8916572591759857'
    while True:
        now_time = datetime.datetime.now().strftime('%H:%M:%S')
        print('现在时间为:'+now_time)
        print('银华日利ETF现在价格为:'+get_current_price(stock_url))
        print('逆回购现在价格为:' + get_current_price(nhg_url))
        print('-'*100)
        if now_time == '09:30:00':
            print('买进')
            buy(by_url,stock_url)
        if now_time == '14:57:00':
            print('卖出')
            sell_yhrl(sell_url,stock_url)
        if now_time == '14:58:00':
            print('卖出逆回购')
            sell_nhg(nhg_sell_url,nhg_url)
        time.sleep(1)

# 启动策略
if __name__ == '__main__':
    strategy()
    
    

    



