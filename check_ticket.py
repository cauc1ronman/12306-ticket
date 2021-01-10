# -*- coding: utf-8 -*-
# author: Jarvis Dong
# email: cauc1ronman@outlook.com
import requests
from urllib.parse import urlencode
import time
import datetime


class Check():
    def __init__(self, date, start, end, purpose):
        self.base_url = 'https://kyfw.12306.cn/otn/leftTicket/queryT?'
        self.url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Cookie': 'JSESSIONID=B709F9775E72BDED99B2EEBB8CA7FBB9; BIGipServerotn=1910046986.24610.0000; RAIL_EXPIRATION=1579188884851; RAIL_DEVIC'
        }
        self.date = date
        self.start_station = start
        self.end_station = end
        if purpose == '学生':
            self.purpose = '0X00'
        else:
            self.purpose = purpose

        # 查找出车站的英文简称，用于构造cookie、完整的余票查询链接

    def look_up_station(self):
        try:  # 可把车站的中英文对照保存下来，下次可直接加载本地文件
            f = open('station.txt', 'r', encoding='utf-8')
            station = f.read()
            station = station.split('@')
            f.close()
        except FileNotFoundError:
            response = requests.get(self.url)
            with open('station.txt', 'w', encoding='utf-8') as f:
                f.write(response.text[len("var station_names ='@"):])
            station = response.text.split('@')
            station.pop(0)

        for each in station:
            i = each.split('|')
            if self.start_station == i[1]:
                self.start_station = i[2]
            elif self.end_station == i[1]:
                self.end_station = i[2]
        return [self.start_station, self.end_station]

    def get_info(self, start_end, check_count,trains):
        # 构造请求参数
        begin_time = time.time()
        trains = ['D3026', 'D3006', 'D3010']
        data = {
            'leftTicketDTO.train_date': self.date,
            'leftTicketDTO.from_station': start_end[0],
            'leftTicketDTO.to_station': start_end[1],
            'purpose_codes': self.purpose
        }
        url = self.base_url + urlencode(data)
        print('完整余票查询链接：', url)
        count = 0  # 用于对车次编号
        while count == 0:
            print('余票查询中...  %d次' % check_count)
            check_time_a = time.time()
            response = requests.get(url, headers=self.headers)
            # print(response.text)
            try:
                json = response.json()
            except ValueError:
                print('余票查询链接有误，请仔细检查！')
                return
            maps = json['data']['map']
            for each in json['data']['result']:
                count += 1
                s = each.split('|')[3:]
                info = {
                    'train': s[0],
                    'start_end': maps[s[3]] + '-' + maps[s[4]],
                    'time': s[5] + '-' + s[6],
                    '历时': s[7],
                    '一等座': s[28],
                    '二等座': s[27]
                }
                try:
                    # 余票的结果有3种：有、一个具体的数字(如：18、6等)、无，判断如果余票是有或者一个具体的数字就直接输出对应的车次信息，然后返回
                    if info['train'] in trains:
                        if info['二等座'] == '有' or int(info['二等座']):
                            print('预定车次信息如下：')
                            print('[%d]' % count, info)
                            end_time = time.time()
                            print('during time:',end_time-begin_time)
                            return count
                    else:
                        print('目标车次暂无！剩余车次如下:{} {}'.format(count,info))

                except ValueError:
                    continue
            count = 0
            check_count += 1
            time.sleep(0.1)
            check_time_b = time.time()
            print('查询耗时：',check_time_b-check_time_a)
