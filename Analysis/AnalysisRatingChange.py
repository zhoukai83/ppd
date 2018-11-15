import sys
sys.path.insert(0, "..")

import json
from UISimulation.PpdUISimulationRequest import PpdUISimulationRequest
from Open.PpdOpenClient import PpdOpenClient
import pandas as pd
from pandas import DataFrame
import datetime

def analysis_rating_chagne():
    # localStorage.removeItem("ppdItem")
    # t = localStorage.getItem("ppdItem") || "[]"; t = JSON.parse(t); $.each($(".listingId"), (key, value) => t.push(parseInt($(value).text()))); localStorage.setItem("ppdItem", JSON.stringify(t)); t

    # file_name = "RatingChange.csv"
    cookies = "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1539574208,1539743508; __utmc=1; token=2c8a8463594dfea0e1aa6a7ef7093f57250c226cb354666c78c0d00f64f06067ba05c0ccf2fcae2ca9; __utma=1.1098278737.1530780657.1540786794.1540874893.54; __utmz=1.1540874893.54.54.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D181030064000097721; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Dg%252fxkxwv6c3pdlrotntqbgqbeel5%252b92jeasbngsgvhnpq6%252f30pvltbim1yuh7oaz77vptulgyriiqgcthx35992pdfgqfbpfthcqw7eo1eluv8ocoi%252bll96ksxz60eem4tcpa22djtij4oyuqoa3sbpmpghdrqvdonme%252bfkpbm3nfbhxlaivwusi2ctp4xzvutl8wyzk9tieiaythr3zmp6vb08jo0la8p4gpqlfioftldgqxuz3l0dvlftlzejpxssourvhb4lxfwbtsy0ltmuq4jevwjpee7jq6cvjutmztp00sp8ry3gmv96zdsb%252fz6k%252fqt%252baw6n%252bepaehqvpc8uhwpfzzao9faoyyjpuaggzgdoan%252bkxw3uc9eqlzuxvk7n0%252beg0iqxr4aqeu8am74bddo78q7wjl6wm%252fhhp8o%252bjxwrduveo09x7daq3%252fh2bda%252ff0nwd93%252bryatpzeo%252bcxmlgtsqlgfarqh6ih6cse6atcczgqnsdzxg5%252ba6te5exic74y84ehte9dhvp9xr91e1%252bpbdh8pttv%252ft8mqfohjbofsiyo6y%252banqlp8tlcb39txpsrr7wsbsu2bku4tysv0b2k3pklxrxv66yzzoacigm8bnfvgk1nzm%252fjgq9knky0snjrc438dvsdo61x2%252bnaavqqcxqn0mtlvelfkbuvvw%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1540535505,1540536242,1540786823,1540874918; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1540874920; currentUrl=https%3A%2F%2Finvdebt.ppdai.com%2Fnegotiable%2Fapply%3Fowingnumber%3D1%2C%26sort%3D7%26level%3D%2Cb%2C%26dueday%3D%26minprincipal%3D%26maxprincipal%3D%26rate%3D%26pageindex%3D6; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1541145692; aliyungf_tc=AQAAAMf723JYfgMAjlD3PKjIVYIDUr25; __tsid=262473610; __vsr=1541990794402.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1541999537938.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1542001509016.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1542162971070.refSite%3Dhttps%3A//invest.ppdai.com/loan/listpage/%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1542166322619.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; __sid=1542249291343.1.1542249291343; waterMarkTimeCheck1=11%2F15%2F2018+10%3A34%3A52"

    file_name = "RatingChange_overDue.csv"
    df_file = pd.read_csv(file_name)

    with open("RatingChange.txt", "r") as f:
        t = f.readlines()
        listing_ids = [int(item.strip()) for item in t]

    print(len(listing_ids), listing_ids)
    client = PpdUISimulationRequest(cookies=cookies)

    json_data = client.pre_apply_debt_list(listing_ids)
    # json_data_str = '{"code":1,"data":{"applyDebtList":[{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":125979520,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":10.24,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":125983680,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122503182,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.21,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"E","listingId":125995511,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126003947,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126004116,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126004829,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126004666,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"E","listingId":126004744,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"D","listingId":126005308,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126007228,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126007630,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126008339,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126009029,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126010086,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126010412,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"E","listingId":126012704,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126016036,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.69,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126016934,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126017932,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126019718,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126024449,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"E","listingId":126026597,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126026349,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126030068,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122628902,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.21,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"D","listingId":126034393,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126035461,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126038768,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126042159,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126042356,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122663631,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.21,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126064996,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.68,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"E","listingId":126072113,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126084379,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"D","listingId":126084346,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126084471,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126084590,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126084708,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126085087,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126086039,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126086217,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"F","listingId":126086200,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126086833,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126086975,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126087351,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126087249,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126087954,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126089558,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126090318,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126089939,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126092449,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122731209,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.20,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122753505,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.20,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122768999,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.20,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122777591,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.20,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122786123,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.20,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126156251,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.66,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":122815327,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.19,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":126181116,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.63,"priceforsaleRate":20.00}],"rateMaxMultiples":20.00,"rateMinMultiples":0.00,"sumAllowanceRadio":0.00,"sumFee":11.36,"sumOwingAmount":2263.14,"sumPriceforsale":2298.62},"netCode":1}'

    # 当前逾期
    # {"code":1,"data":{"applyDebtList":[{"allowanceRadio":0.00,"currentCreditCode":"G","listingId":125257334,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":42.72,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":121727301,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.22,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":128608088,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":50.85,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":128493838,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":50.88,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":121611281,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.23,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":121463781,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.24,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":121514001,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.24,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":121372383,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.25,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"C","listingId":121365243,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.25,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"B","listingId":121401675,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":34.53,"priceforsaleRate":20.00},{"allowanceRadio":0.00,"currentCreditCode":"E","listingId":120974900,"maxRate":40.00,"minRate":20.00,"preDebtDealId":0,"priceforsale":17.28,"priceforsaleRate":20.00}],"rateMaxMultiples":20.00,"rateMinMultiples":0.00,"sumAllowanceRadio":0.00,"sumFee":1.51,"sumOwingAmount":294.55,"sumPriceforsale":299.69},"netCode":1}
    print(json.dumps(json_data))
    # json_data = json.loads(json_data_str)

    count = 0

    datas = []

    for item in json_data:
        if item["currentCreditCode"] in ["D", "E", "F", "G"]:
            print(item["listingId"], "Changed to", item["currentCreditCode"], item["priceForSale"])
            count += 1

        if item["minRate"] == 20:
            item["origin"] = "B"
        elif item["minRate"] == 24:
            item["origin"] = "C"
        elif item["minRate"] == 16:
            item["origin"] = "A"
        else:
            print(f"warning, can not guess origin: {item['listingId']} {item['minRate']}")
        item["testDate"] = datetime.datetime.today().strftime('%Y-%m-%d')
        datas.append(item)

    df = DataFrame(datas)
    df = pd.concat([df_file, df], ignore_index=True, sort=False)
    df.to_csv(file_name, index=False)
    print(count)

def main():
    analysis_rating_chagne()

    # open_client = PpdOpenClient(key_index=1)
    # open_client.batch_get_listing_info([])
    pass

if __name__ == "__main__":
    main()