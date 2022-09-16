import requests
import datetime
from bs4 import BeautifulSoup
import json
import prettytable as pt


def get_config():
    with open('config.json', encoding='utf-8') as f:
        _config = json.load(f)
    return _config


def post(client: str, room_name: str, room_id: str, interval: int = 7) -> list:
    # 获取网页源码信息
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        }
    url = 'http://192.168.84.3:9090/cgcSims/selectList.do'
    today = datetime.date.today()
    day_before = str(today - datetime.timedelta(days=interval+1))
    today = str(today)
    params = {
        'hiddenType': '',
        'isHost': '0',
        'beginTime': day_before,
        'endTime': today,
        'type': '2',
        'client': client,
        'roomId': room_id,
        'roomName': room_name,
        'building': ''
    }

    response = requests.post(url, data=params, headers=headers)
    response.encoding = 'gbk'
    return response.text


def anl_html(text):

    # 对于网页源代码进行分析
    soup = BeautifulSoup(text, 'html.parser')
    soup_data = soup.find_all('td', width='13%', align='center')
    soup_data = [c.text for c in soup_data]  # 获取对网页源码进行信息提取，去除html代码
    soup_datetime = soup.find_all('td', width='22%', align='center')
    soup_datetime = [c.text for c in soup_datetime]

    # 文本中符号去除保留有效数据
    for i in range(len(soup_data)):
        soup_data[i] = soup_data[i].strip()
    for i in range(len(soup_datetime)):
        soup_datetime[i] = soup_datetime[i].strip()
    date = soup_datetime[1:]
    data = soup_data[3:]

    buffer = []
    for i in range(0, len(data), 5):  # 这里需要讲解
        b = data[i:i + 5]
        buffer.append(b)
    data = buffer

    data_table=[]
    for i in range(int(len(date))):
        if i ==0:
            data_table.append({
                '日期':date[i],
                '剩余电量':data[i][2],
                '当日使用':'-',
                '当日充值':'-'
            })
        else:
            data_table.append({
                '日期': date[i],
                '剩余电量': data[i][2],
                '当日使用': round(float(data[i][3])-float(data[i-1][3]),2),
                '当日充值': round(float(data[i][4])-float(data[i-1][4]),2)
            })
    table=pt.PrettyTable(['日期','剩余电量','当日使用','当日充值'])
    for i in range(int(len(date))):
        if i !=0:
            table.add_row([data_table[i]['日期'],data_table[i]['剩余电量'],data_table[i]['当日使用'],data_table[i]['当日充值']])



    # 测试代码
    print(table)


def main():
    config = get_config()
    client = config['client']
    room_id = config['room_id']
    room_name = config['room_name']
    interval_day = config['interval_day']
    if room_name == '' or room_id == '':
        print('未配置json文件')
        exit()
    html = post(client, room_name, room_id, interval_day)
    if len(html) == 0:
        print('爬取失败')
        exit()
    anl_html(html)


if __name__ == '__main__':
    main()
