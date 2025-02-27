import requests
import time
from multiprocessing import Pool
from lxml import etree
import pandas as pd


def get_home_url(page):
    url = 'https://hz.esf.fang.com/house/i{}/'.format(page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Cookie': 'lianjia_uuid=3c7c16db-579a-4e60-baa3-241dce90e646; crosSdkDT2019DeviceId=t33bhp-fws840-hfx7fouh4s3i7wj-mx8squngz; _ga=GA1.2.821433405.1734174752; __xsptplus788=788.1.1734174752.1734176105.7%234%7C%7C%7C%7C%7C%23%23%23; ftkrc_=e1cf2de7-579b-45a0-b909-421ff219362c; lfrc_=d26f63ce-370c-4ca1-9f0d-fa2ea4cccc7f; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22193c4de5bf55c0-0af123954c0b78-7e433c49-1764000-193c4de5bf625d3%22%2C%22%24device_id%22%3A%22193c4de5bf55c0-0af123954c0b78-7e433c49-1764000-193c4de5bf625d3%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22biying%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wymoren%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; ke_uuid=1c960bf4327727bc86c10a94c4d6d00a; lianjia_ssid=2e198e6e-8521-4568-b349-2a5ae8a7b11c; login_ucid=2000000459021577; lianjia_token=2.0011597ce346a60c0600f455d28fb387e5; lianjia_token_secure=2.0011597ce346a60c0600f455d28fb387e5; security_ticket=cGrr61HRXErVEpKb1PRH/h7JwB/pX9Hnsbvyh26h487FBfDuJrKyNqXkLY+P8pf07GzN00CsKLIQCSiOXuyKD1JDXGmmZwhcAVz+WSc1PqgOQnY3u0elv28MZa2e8/9smDTStRG+DzzRQFv5yuz9mq4SOqdRvTBy+lKq6l8m92U=; Hm_lvt_b160d5571570fd63c347b9d4ab5ca610=1737449171,1737540930,1738076952,1739001231; HMACCOUNT=C437DD3419895A2B; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZTJiZjU1MzkzN2FmZDVlZWUzODk5OTQzZGVjOTVhZmRmZjBjM2U0ZTE2MzdjZmJiOTI2ZjkwMmE0MTk0MjA5NGYzNzJkYTI2NjFmY2JlNzMxYzA3Yjc1ZDk4NjcwMjAzOWMzMjc0NTliN2U5YWIzMzdkMWEzMDRjZGRlMDQwZTRjZjAwNjU3Y2JhYWVhZmQ4NjE3ZTE1MzY2NThhZGFkYTBiYTkyZjM1NzQ4OGQyYjgyMjBlN2UwOWQ4M2UzMDk0MjExZDVmMzA4ZGVkMzE0ODI1M2Y2ODA5ZTUzYWFiNGIwZWE2NTQ2YjU1OWJhNjZlMWE4ODg5NTlhZTZhMGJmZlwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI5OGQ4NTI2ZVwifSIsInIiOiJodHRwczovL3NoLmtlLmNvbS9lcnNob3VmYW5nLzEwNzExMTg1OTUwNS5odG1sP2ZiX2V4cG9faWQ9OTQwNjM2NTU0Mjc0OTUxMTY4Iiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=; digv_extends=%7B%22utmTrackId%22%3A%22%22%7D; select_city=310000; Hm_lpvt_b160d5571570fd63c347b9d4ab5ca610=1739001319'    }
    text = requests.get(url,headers=headers).text
    html = etree.HTML(text)
    detail_url = html.xpath('//h4[@class="clearfix"]/a/@href')
    return detail_url

# 获取房源详细数据信息
def get_home_detail_infos(detail_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Cookie': 'lianjia_uuid=3c7c16db-579a-4e60-baa3-241dce90e646; crosSdkDT2019DeviceId=t33bhp-fws840-hfx7fouh4s3i7wj-mx8squngz; _ga=GA1.2.821433405.1734174752; __xsptplus788=788.1.1734174752.1734176105.7%234%7C%7C%7C%7C%7C%23%23%23; ftkrc_=e1cf2de7-579b-45a0-b909-421ff219362c; lfrc_=d26f63ce-370c-4ca1-9f0d-fa2ea4cccc7f; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22193c4de5bf55c0-0af123954c0b78-7e433c49-1764000-193c4de5bf625d3%22%2C%22%24device_id%22%3A%22193c4de5bf55c0-0af123954c0b78-7e433c49-1764000-193c4de5bf625d3%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22biying%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wymoren%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; ke_uuid=1c960bf4327727bc86c10a94c4d6d00a; lianjia_ssid=2e198e6e-8521-4568-b349-2a5ae8a7b11c; login_ucid=2000000459021577; lianjia_token=2.0011597ce346a60c0600f455d28fb387e5; lianjia_token_secure=2.0011597ce346a60c0600f455d28fb387e5; security_ticket=cGrr61HRXErVEpKb1PRH/h7JwB/pX9Hnsbvyh26h487FBfDuJrKyNqXkLY+P8pf07GzN00CsKLIQCSiOXuyKD1JDXGmmZwhcAVz+WSc1PqgOQnY3u0elv28MZa2e8/9smDTStRG+DzzRQFv5yuz9mq4SOqdRvTBy+lKq6l8m92U=; Hm_lvt_b160d5571570fd63c347b9d4ab5ca610=1737449171,1737540930,1738076952,1739001231; HMACCOUNT=C437DD3419895A2B; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZTJiZjU1MzkzN2FmZDVlZWUzODk5OTQzZGVjOTVhZmRmZjBjM2U0ZTE2MzdjZmJiOTI2ZjkwMmE0MTk0MjA5NGYzNzJkYTI2NjFmY2JlNzMxYzA3Yjc1ZDk4NjcwMjAzOWMzMjc0NTliN2U5YWIzMzdkMWEzMDRjZGRlMDQwZTRjZjAwNjU3Y2JhYWVhZmQ4NjE3ZTE1MzY2NThhZGFkYTBiYTkyZjM1NzQ4OGQyYjgyMjBlN2UwOWQ4M2UzMDk0MjExZDVmMzA4ZGVkMzE0ODI1M2Y2ODA5ZTUzYWFiNGIwZWE2NTQ2YjU1OWJhNjZlMWE4ODg5NTlhZTZhMGJmZlwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI5OGQ4NTI2ZVwifSIsInIiOiJodHRwczovL3NoLmtlLmNvbS9lcnNob3VmYW5nLzEwNzExMTg1OTUwNS5odG1sP2ZiX2V4cG9faWQ9OTQwNjM2NTU0Mjc0OTUxMTY4Iiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=; digv_extends=%7B%22utmTrackId%22%3A%22%22%7D; select_city=310000; Hm_lpvt_b160d5571570fd63c347b9d4ab5ca610=1739001319'    }
    detail_text = requests.get(detail_url,headers=headers).text
    html = etree.HTML(detail_text)
    all_data = []
    # 解析获取相关数据
    # 所在地址
    home_location = html.xpath('//div[@class="rcont"]//text()')
    all_data.append(home_location[0])#小区id
    all_data.append(home_location[-2])#所在市
    all_data.append(home_location[-1])#具体位置
    # 总价格
    total_price = html.xpath('/html/body/div[4]/div[1]/div[4]/div[1]/div[1]/div[1]//text()')
    all_data.append(total_price[0]+'万')
    # 基本信息
    data_house = html.xpath('//div[@class="tr-line clearfix"]//div[@class="tt"]//text()')
    all_data.append(data_house[0])#户型
    all_data.append(data_house[1])#占地
    all_data.append(data_house[2])#单价
    all_data.append(data_house[3])#朝向
    all_data.append(data_house[4])#楼层
    all_data.append(data_house[5])#装修
    res_url=detail_url#网址
    all_data.append(res_url)
    return all_data


# 数据保存至csv文件里（使用pandas中的to_csv保存）
def save_data(data):
    data_frame = pd.DataFrame(data,columns=['小区名称','所在市','具体位置','房屋总价','户型','占地','单价','朝向','楼层','装修','网址'])
    print(data_frame)
    data_frame.to_csv('hangzhou_fang.csv',header=False,index=False,mode='a',encoding='utf_8_sig')

def main(page):
    print('开始爬取第{}页的数据！'.format(page))
    
    urls = get_home_url(page)
    for url in urls:
        print('开始爬去详细网页为{}的房屋详细信息资料！'.format(url+'l'))
        all_data = get_home_detail_infos(detail_url='https://hz.esf.fang.com'+url+'l')
        data = []
        data.append(all_data)
        save_data(data)


if __name__ == "__main__":
    # page = range(31,39)
    # print('爬虫开始')
    # for p in page:
    #     main(p)
    # print("爬虫结束")
    page = range(363,399)
    print('爬虫开始')
    for p in page:
        main(p)
    print("爬虫结束")
    print("最后一次")
    main(3100)
    print("爬虫结束")