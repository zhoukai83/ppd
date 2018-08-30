#encoding='utf-8'
import requests
import json
import time
import os
import pandas as pd
from pandas import DataFrame, Series

config_file = json.load(open("config.json", "r"))

headers = {
    "Host": "invest.ppdai.com",
    "Connection": "keep-alive",
    "Content-Length": "36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://invest.ppdai.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": "https://invest.ppdai.com/loan/info/" + "122337316",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": "aliyungf_tc=AQAAADLCS1DymggAjlD3PC6nxhYoLb8H; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164c55a3734e12-0e8029f1590cf3-5b193613-2304000-164c55a373594b%22%2C%22%24device_id%22%3A%22164c55a3734e12-0e8029f1590cf3-5b193613-2304000-164c55a373594b%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D",
}

headers["Cookie"] = config_file["Cookie"]

url = "https://invest.ppdai.com/api/invapi/LoanDetailWithNoAuthPcService/showBaseInfoWithNoAuth"


def flat_json(jsonData, parentKey=None):
    flat_dict = {}
    for key in jsonData:
        if type(jsonData[key]).__name__ == 'dict':
            if parentKey:
                temp = flat_json(jsonData[key], parentKey + "_" + key)
                flat_dict = {**flat_dict, **temp}
            else:
                temp = flat_json(jsonData[key], key)
                flat_dict = {**flat_dict, **temp}
        else:
            if parentKey:
                flat_dict[parentKey + "_" + key] = jsonData[key]
            else:
                flat_dict[key] = jsonData[key]

    return flat_dict

def main():
    session = requests.Session()

    # url = "https://invest.ppdai.com/loan/info/122343448"

    start = time.clock()
    # 91337318
    id_start = 91367226
    index = 91387126
    store_list = []
    for index in range(121396680, 121396684):
        # id = index + id_start

        if (index % 2) == 0:
            print(index)
        file_name = 'data/{0}.json'.format(index)
        headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(index)

        if os.path.exists(file_name):
            continue

        req = session.post(url, data = '{"listingId":"' + str(index) + '","source":1}', headers = headers)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(req.text)

    end = time.clock()

    print(index)
    with open('data2/{1}_{0}.json'.format(index), 'w', encoding='utf-8') as f:
        f.write(json.dumps(store_list))
    print(end-start)


def get_pay_record(id, cookie):
    file_name = "data/showPayAndCommRecord/showPayAndCommRecord_{0}.json".format(id)
    post_data = '{"authenticated":true, "listingId":"' + str(id) + '","source":1}'

    if os.path.exists(file_name):
        print(id, "exist")
        return

    print(id)
    headers_pay = {
        "Host": "invest.ppdai.com",
        "Connection": "keep-alive",
        "Content-Length": "36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://invest.ppdai.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://invest.ppdai.com/loan/info/" + str(id),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "",
    }
    headers_pay["Cookie"] = cookie
    headers_pay["Referer"] = "https://invest.ppdai.com/loan/info/" + str(id)
    url_pay = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showPayAndCommRecord"

    session = requests.Session()

    req = session.post(url_pay, data=post_data, headers=headers_pay)

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(req.text)

def get_show_borrower_statistics(id, cookie):
    file_name = "data/showBorrowerStatistics/showBorrowerStatistics_{0}.json".format(id)
    if os.path.exists(file_name):
        print(id, "exist")
        return

    print(id)
    headers_pay = {
        "Host": "invest.ppdai.com",
        "Connection": "keep-alive",
        "Content-Length": "35",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://invest.ppdai.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://invest.ppdai.com/loan/info/" + str(id),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "",
    }
    headers_pay["Cookie"] = "regSourceId=0; referID=0; fromUrl=; referDate=2018-7-5%2015%3A24%3A50; gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1530775491; aliyungf_tc=AQAAAB8EXBGM3wAAjlD3PFfDXfOR3zI9; __fp=fp; __vid=3407234.1530775507276; ppdaiRole=4; __utmc=1; token=75df8035594dfea0e1aa6a7ef7093f575ec722e784af3110df7280df4b786ad2a861bdf6c15ba7299e; __eui=Cel3wwogQQUMvl7O%2BveuJQ%3D%3D; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; _ppdaiWaterMark=15312861763999; __utma=1.1098278737.1530780657.1532312898.1532400343.18; __utmz=1.1532400343.18.18.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D180724064000080614; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Djesqwtm1nleckrrjkrcngjfspe4uajhukwquhpw1%252b%252f8xu%252fxq%252b3jgwhzxkomlk9godaa6cdt5l9dgwc%252bok1ng9sbnatsmdqtdptb3vmccln2focaal23dznognu49afer6gr%252bypmrbeub5qcqxjlscr8t8pkdxwgcvjiaxk2rbdolprs%252b8pmfmoqj4a%252b3atei1lel1sxt5qysn5c3siqniljvqrlfcbuuslgze5riygsyy7eiehdewaemxtl8ctgkmrekgnr7rumdzgzlo9zrul5%252fqolxjsps4lfxfboiqstbi6xi2t32pugydyiyjfyp2yu6jbitwbrsz%252feobnk4mqjaphvzcbbzs8x%252fi2zda%252bupfglj2%252b%252ffe7jrr0ovqfi5eqwywcv4ozf6xojnif9gzbuq%252byg31sid9jft9juqqdj0wsjuuqwhiuy03iedfam56%252f77vc2dpmcbdl0tq37dhy9lfpwmusyimh4fh7vv4lmfmwlxoncbk9aaix%252b4luvwm%252fjdwbd9be2jpbuo848h91slvod4dqd%252fdoc92xakzbugs1zjnjed6ivox8xrlb40oannp3motypaqykhmin2sezmyifc4xeobakizxzjyfemgh%252fgfhaqov8%252bc8qutmarc7tsbhvzzknxpumcn6%252fu%252fnqibbxnumgmcxsqiosa2ni%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1531967735,1532063497,1532312929,1532400368; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1532400370; __tsid=200643318; noticeflag=true; __vsr=1532063468981.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1532312898092.refSite%3Dhttps%3A//www.ppdai.com/moneyhistory%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1532412203002.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1532491933145.refSite%3Dhttps%3A//www.ppdai.com/moneyhistory%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1532498277585.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; currentUrl=https%3A%2F%2Finvest.ppdai.com%2Findex%2Fnotfound; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1532498392; JSESSIONID=9517CB4418CBCD1D77F3E88583D94142"
    headers_pay["Referer"] = "https://invest.ppdai.com/loan/info/" + str(id)
    url_pay = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerStatistics"

    session = requests.Session()
    req = session.post(url_pay, data='{"listingId":"' + str(id) + '","source":1}', headers=headers_pay)

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(req.text)

def get_show_borrow_info(id, cookie):
    file_name = "data/showBorrowerInfo/showBorrowerInfo_{0}.json".format(id)

    if os.path.exists(file_name):
        print(id, "exist")
        return

    print(id)
    headers_pay = {
        "Host": "invest.ppdai.com",
        "Connection": "keep-alive",
        "Content-Length": "35",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://invest.ppdai.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://invest.ppdai.com/loan/info/" + str(id),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "",
    }
    headers_pay["Cookie"] = cookie
    headers_pay["Referer"] = "https://invest.ppdai.com/loan/info/" + str(id)
    url_pay = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerInfo"

    session = requests.Session()
    req = session.post(url_pay, data='{"listingId":"' + str(id) + '","source":1}', headers=headers_pay)

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(req.text)

def get_all_pay_record(file_name, cookie):
    df = pd.read_csv(file_name, encoding="utf-8")
    df.resultContent_listing_listingId = df.resultContent_listing_listingId.astype(int)
    df.resultContent_listing_listingId.apply(lambda x: get_pay_record(x, cookie))

def get_all_browser_info(file_name, cookie):
    df = pd.read_csv(file_name, encoding="utf-8")
    df.listingId = df.listingId.astype(int)
    df.listingId.apply(lambda x: get_show_borrow_info(x, cookie))

def combine_file(start):
    file_dir = "data/data923-925"
    records = []

    if not os.path.exists("data/data_combine_{0}".format(start - 1)):
        os.makedirs("data/data_combine_{0}".format(start - 1))

    id_start = (start - 1) * 1000 + 1
    id_end = id_start + 100000
    print(id_start, id_end)
    for id in range(id_start, id_end):
        file_name = '{1}/{0}_200.json'.format(id, file_dir)
        first_file_exist = os.path.exists(file_name)
        second_file_exist = False
        # print(id)
        if not first_file_exist:
            second_file_exist = os.path.exists( '{1}/{0}.json'.format(id, file_dir))

        if first_file_exist or second_file_exist:

            try:
                if first_file_exist:
                    jsonData = json.load(open(file_name, "r", encoding='utf-8'))
                else:
                    jsonData = json.load(open('{1}/{0}.json'.format(id, file_dir), "r", encoding='utf-8'))
                records.append(jsonData)
            except Exception as e:
                print(id, e)

            if (id % 1000) == 0:
                print("save", id)
                with open('data/data_combine_{1}/{0}.json'.format(id, start - 1), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(records, ensure_ascii=False))
                records = []
        else:
            print(file_name, "noteexist")

    if len(records) != 0:
        print("left records")
        with open('data/{0}.json'.format("left"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(records, indent=4, ensure_ascii=False))
    print("finish")
    None


def save_to_csv_100(start):
    import os
    records = []

    not_exist = []
    for index in range(start, start+1000):
        #     id = index + id_start

        file_name = 'data/data_combine_100_925-927/{0}.json'.format(index*100)
        if os.path.exists(file_name):
            jsonData = json.load(open(file_name, "r", encoding='utf-8'))
            for item in jsonData:
                records.append(flat_json(item))
        else:
            not_exist.append(file_name)
            print(file_name, "not exist")

    print("total not exist:", not_exist)
    df = DataFrame(records)
    df_simple_finish = df[df.resultContent_listing_creditCode.notnull()]
    print(df_simple_finish.shape)
    df_simple_finish.to_csv("finishData/{0}.csv".format((start - 1) / 10), encoding="utf-8")
    print("finish")


def save_to_csv(start):
    import os
    records = []
    for index in range(start, start+100):
        #     id = index + id_start

        file_name = 'data/data_combine_{1}/{0}.json'.format(index*100, start-1)
        if os.path.exists(file_name):
            jsonData = json.load(open(file_name, "r", encoding='utf-8'))
            for item in jsonData:
                records.append(flat_json(item))
        else:
            print(file_name, "not exist")

    df = DataFrame(records)
    df_simple_finish = df[df.resultContent_listing_creditCode.notnull()]
    print(df_simple_finish.shape)
    df_simple_finish.to_csv("finishData/{0}.csv".format(start - 1), encoding="utf-8")
    print("finish")
# jsonData = json.load(open('data/1_combine.json', "r", encoding='utf-8'))
# print(jsonData)

if __name__ == "__main__":
    # main()
    cookie = "regSourceId=0; referID=0; fromUrl=; referDate=2018-7-5%2015%3A24%3A50; gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1530775491; aliyungf_tc=AQAAAB8EXBGM3wAAjlD3PFfDXfOR3zI9; __fp=fp; __vid=3407234.1530775507276; ppdaiRole=4; __utmc=1; token=75df8035594dfea0e1aa6a7ef7093f575ec722e784af3110df7280df4b786ad2a861bdf6c15ba7299e; __eui=Cel3wwogQQUMvl7O%2BveuJQ%3D%3D; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; _ppdaiWaterMark=15312861763999; __utma=1.1098278737.1530780657.1532312898.1532400343.18; __utmz=1.1532400343.18.18.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D180724064000080614; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Djesqwtm1nleckrrjkrcngjfspe4uajhukwquhpw1%252b%252f8xu%252fxq%252b3jgwhzxkomlk9godaa6cdt5l9dgwc%252bok1ng9sbnatsmdqtdptb3vmccln2focaal23dznognu49afer6gr%252bypmrbeub5qcqxjlscr8t8pkdxwgcvjiaxk2rbdolprs%252b8pmfmoqj4a%252b3atei1lel1sxt5qysn5c3siqniljvqrlfcbuuslgze5riygsyy7eiehdewaemxtl8ctgkmrekgnr7rumdzgzlo9zrul5%252fqolxjsps4lfxfboiqstbi6xi2t32pugydyiyjfyp2yu6jbitwbrsz%252feobnk4mqjaphvzcbbzs8x%252fi2zda%252bupfglj2%252b%252ffe7jrr0ovqfi5eqwywcv4ozf6xojnif9gzbuq%252byg31sid9jft9juqqdj0wsjuuqwhiuy03iedfam56%252f77vc2dpmcbdl0tq37dhy9lfpwmusyimh4fh7vv4lmfmwlxoncbk9aaix%252b4luvwm%252fjdwbd9be2jpbuo848h91slvod4dqd%252fdoc92xakzbugs1zjnjed6ivox8xrlb40oannp3motypaqykhmin2sezmyifc4xeobakizxzjyfemgh%252fgfhaqov8%252bc8qutmarc7tsbhvzzknxpumcn6%252fu%252fnqibbxnumgmcxsqiosa2ni%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1531967735,1532063497,1532312929,1532400368; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1532400370; __tsid=200643318; noticeflag=true; __vsr=1532063468981.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1532312898092.refSite%3Dhttps%3A//www.ppdai.com/moneyhistory%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1532412203002.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1532491933145.refSite%3Dhttps%3A//www.ppdai.com/moneyhistory%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1532498277585.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; currentUrl=https%3A%2F%2Finvest.ppdai.com%2Findex%2Fnotfound; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1532498392; JSESSIONID=4A1D4E0F7A963872EBD0B65C7709995A"
    # start = 92401
    # combine_file(start)
    # save_to_csv(start)

    # save_to_csv_100(926001)

    # get_pay_record(91500227, cookie)
    # get_all_pay_record("finishData/915-922_B_6.csv", cookie)
    # print(headers)

    # get_show_borrow_info(91502591, cookie)
    get_all_browser_info("finishData/915-922_B_6.csv", cookie)

