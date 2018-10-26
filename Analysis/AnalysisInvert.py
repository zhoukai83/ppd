# -*- coding: utf-8 -*-
import requests
import json
import pandas as pd
from pandas import DataFrame
import datetime
import time

def get_list():
    df_old = pd.read_csv("invert.csv")
    with open("invert.json", encoding="utf-8") as f:
        json_data = json.load(f)

    df = DataFrame(json_data)

    del df["avatarUrl"]
    del df["userIdStr"]
    del df["followFlag"]
    print(df)

    df = pd.concat([df_old, df])
    df.to_csv("invert.csv", index=False)


def get_detail(invert_user_id):
    session = requests.session()
    headers = {
        "Host": "strategy.ppdai.com",
        "Connection": "keep-alive",
        # "Content-Length": "959",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://invstrat.ppdai.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://invstrat.ppdai.com/inverstDetail/53648",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; regSourceId=0; referID=0; fromUrl=https%3A%2F%2Fwww.ppdai.com%2Fmoneyhistory; referDate=2018-10-8%2010%3A44%3A40; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; aliyungf_tc=AQAAAIYUQkBSXQYAjlD3PH1A9uJL9A27; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1539574208,1539743508; __utmc=1; __vsr=1540262365101.refSite%3Dhttps%3A//invstrat.ppdai.com/strategyMarket%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1540265859551.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1540281688827.refSite%3Dhttps%3A//invstrat.ppdai.com/strategyMarket%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1540286720139.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1540350163781.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; token=2c8a8463594dfea0e1aa6a7ef7093f57250c226cb354666c78c0d00f64f06067ba05c0ccf2fcae2ca9; __utma=1.1098278737.1530780657.1539942197.1540350217.47; __utmz=1.1540350217.47.47.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D181024064000076838; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Dvq1s%252fugzwmseg9kxyggqbyufawgiwkyh8flf5dtjdwmgti5kxzwihkq%252fgosr%252fmvbjllpmogb2xqfsag94245bgw13ox4a8p6lquhtqdz39xtfgz%252fclrww4igszp1ni2ucnfxhtjienwckhqmy2xqri0ccut3v%252bbajy%252bqzadjikay4kqmxheg4jmr0trmzkqj%252bucbk25jeolzciecfybzbm6ynvk9ldcb3nt4wi%252bdkvgzjgw6gfihcbmcm%252flkv0zqrgmrjsmdin%252fef28nzdl7peoqgzxrftck0ovlxqevcbnrdpg%252ftcxkyoolno5vb3p7r%252b%252fk%252fbm5t5aasdccfbfb83rsociffmpvs6kwsdtiomcm7515hlnjpa4owzahk1nkc%252fsz4t5ktgwmup43vazocfs%252f%252ftoqeugrvoj7rsa9lyowrzuuzpyqdqeg3idxi0cvhidw5dqfrdqqr%252fnmm5an71vsj%252fvvkxbj5gyemwbmenmkh6f1scphwnytgyevtpdne9ohlkftgnuw0vurx7ffjmrlmbrinrrxpd0p7tqfoo2j6updve4rbwgy%252b7fewobqvdsz4yfarnl30zbpmuc0amukanpnggdbar5oqqidfsgbxy4oxw4qxcpvkf4aitvc1teycq2rjv2dpvbjkkb47fxbc0r0d4ine5t5clyblwi%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1539940159,1539940326,1539942229,1540350246; payDatetimeCookie=2018-10-24+11%3a03%3a08; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1540350249; currentUrl=https%3A%2F%2Finvdebt.ppdai.com%2Fnegotiable%2Fapply%3Fowingnumber%3D1%2C%26sort%3D%26level%3D%2Cb%2C%26dueday%3D%26minprincipal%3D%26maxprincipal%3D%26rate%3D%26pageindex%3D7; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1540353216; __tsid=249418207; waterMarkTimeCheck1=10%2F24%2F2018+15%3A58%3A46; __sid=1540367924771.2.1540367944998",
    }
    response = session.post("https://strategy.ppdai.com/forward/forwardreq", data=f"Target=financialplanner-getFinancialPlanner&RequestBody=%7B%22userid%22%3A%22{invert_user_id}%22%7D", headers=headers)
    result = response.text

    # result = '{"result":0,"resultMessage":"成功","data":{"id":null,"page":1,"rows":10,"userid":53648,"score":null,"checkStatus":1,"name":"","followFlag":true,"yieldRate":0.1830,"popularity":2505,"sumBidAmount":10950576,"registerData":1228609016000,"introduction":"拍拍贷9年投资经验，累积年化收益率20%以上","avatarUrl":"https://jc01.info.user.ppdai.com/31a8d6e825264bdb9cb07aedc9c2707e.JPG","nickName":"日久"}}'
    print(result)
    json_data = json.loads(result)
    detail_data = json_data.get("data")

    myNumber = detail_data.get("registerData")
    print(detail_data.get("yieldRate") * 100, detail_data.get("sumBidAmount"), myNumber, datetime.datetime.fromtimestamp(myNumber / 1000.0).strftime('%Y-%m-%d'))
    return detail_data.get("yieldRate") * 100,  detail_data.get("sumBidAmount"), datetime.datetime.fromtimestamp(myNumber / 1000.0).strftime('%Y-%m-%d')


def get_all_detail():
    df = pd.read_csv("invert_detail.csv")
    # df["yieldRate"] = -1.1
    # df["sumBidAmountDetail"] = -1
    # df["registerDate"] = "Unknow"
    count = 0
    for index, row in df.iterrows():
        count += 1

        if row["yieldRate"] > 0:
            print(index, row['userId'], row["yieldRate"])
            continue

        print(index, row['userId'])

        # if count >= 1:
        #     break
        yield_rate, sum_bid_amount, register_time = get_detail(row["userId"])
        print(yield_rate)
        df.at[index, 'yieldRate'] = yield_rate
        df.at[index, 'sumBidAmountDetail'] = sum_bid_amount
        df.at[index, 'registerDate'] = register_time
        df.to_csv("invert_detail.csv", encoding="utf-8")

        time.sleep(3)

def main():
    with open("strategylist.json", encoding="utf-8") as f:
        json_data = json.load(f)
        print(json_data)

        df = DataFrame(json_data)
        df.to_csv("strategylist.csv", index=False, encoding="utf-8")
    # get_detail(6110694)
    pass

if __name__ == "__main__":
    main()