import requests
import json
import pymysql.cursors
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
connect = pymysql.Connect(host='localhost',
                          port=3306,
                          user='root',
                          passwd='root',
                          db='automobai',
                          charset='utf8'
                          )
# 获取游标
cursor = connect.cursor("")
name = "auto"+time.strftime('%Y%m%d%H%M',time.localtime(time.time()))

cursor.execute("CREATE TABLE `%s` (`id` int(11) NOT NULL AUTO_INCREMENT, `time` varchar(45) DEFAULT NULL,`bikeIds` varchar(45) DEFAULT NULL,  `biketype` varchar(45) DEFAULT NULL,  `distance` varchar(45) DEFAULT NULL,  `distId` varchar(45) DEFAULT NULL,`distNum` varchar(45) DEFAULT NULL,  `distX` varchar(45) DEFAULT NULL,  `distY` varchar(45) DEFAULT NULL,  `type` varchar(45) DEFAULT NULL,  PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"%(name))
# 如果headers里面没有referer则会访问异常
# referer表示上一个页面是什么。
headers = {
    'User-Agent': 'MicroMessenger/6.5.7.1041 NetType/WIFI Language/zh_CN',
    'referer': 'https://servicewechat.com/wx80f809371ae33eda/36/',
    'content-type': 'application/x-www-form-urlencoded'
}
url = 'https://mwx.mobike.com/mobike-api/rent/nearbyBikesInfo.do'

zuo=108.68
you=109.15
xia=34.05
shang=34.42
step = 0.005
i=0


def frange(x, y, jump):
    while x < y:
        yield x
        x += jump

for jindu in frange(zuo,you,step):
    for weidu in frange(xia, shang, step):
        i=i+1
        data = {
            'longitude': jindu,  # 经度
            'latitude': weidu,  # 纬度
            'citycode': '029',
            'errMsg': 'getMapCenterLocation:ok',
            'wxcode':'013DYXZk2bFvQH0KTJ0l29lSZk2DYXZZ'
        }

        try:
            z = requests.post(url, data=data, headers=headers, verify=False, timeout=0.1)
        except Exception as e:
            print('第', i, '次请求超时','  正在重试')
            try:
                z = requests.post(url, data=data, headers=headers, verify=False, timeout=0.1)
            except Exception as e:
                print('第', i, '次请求超时', '  正在重试')
                try:
                    z = requests.post(url, data=data, headers=headers, verify=False, timeout=0.2)
                except Exception as e:
                    print('第', i, '次请求超时', '  正在重试')
                    try:
                        z = requests.post(url, data=data, headers=headers, verify=False, timeout=0.3)
                    except Exception as e:
                        print('第', i, '次请求超时', '  正在重试')
                        try:
                            z = requests.post(url, data=data, headers=headers, verify=False, timeout=1)
                        except Exception as e:
                            print('第', i, '次请求超时', '  正在重试')
                            z = requests.post(url, data=data, headers=headers, verify=False)

        finally:
            print('第', i, '次请求成功')

        try:
            data = z.json()
            data = json.dumps(data)
            data = json.loads(data)
            datadic = data['object']
        except Exception as e:
            print('第', i, '次迭代没有结果',"jindu",jindu," weidu=",weidu,)
            datadic={}
        finally:
            date = z.headers['Date']
        for dd in datadic:
            try:
           #     str="insert into %s"%name+" (time ,bikeIds, biketype,distance,distId,distNum,distX,distY,type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(
                    'insert into ''%s'%name+'(time ,bikeIds, biketype,distance,distId,distNum,distX,distY,type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (date, dd['bikeIds'], dd['biketype'], dd['distance'], dd['distId'], dd['distNum'], dd['distX'],
                     dd['distY'], dd['type']))

            except Exception as e:
                connect.rollback()  # 事务回滚
                print('写入数据库失败', e)
            else:
                connect.commit()  # 事务提交
        print('写入数据库成功', cursor.rowcount)
        print("jindu+", jindu, " weidu=", weidu, '第', i, '次迭代')

print('已经完成全部数据爬取')
cursor.close()
connect.close()
