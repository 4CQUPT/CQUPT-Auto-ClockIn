import json
import random

import requests
from requests.adapters import HTTPAdapter
from urllib.parse import quote

import ulits

# 超时重试 3 次
log = ulits.Logger('all.log',level='debug').logger
s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=3))

wecqupt_api = "https://we.cqupt.edu.cn/api"
urls = {
    "post_mrdk": wecqupt_api + "/mrdk/post_mrdk_info.php",
    "get_mrdk": wecqupt_api + "/mrdk/get_mrdk_flag.php",
    "post_get_student": wecqupt_api + "/get_student_info.php",
    "get_location": "https://apis.map.qq.com/ws/geocoder/v1/",
    "push": {
        "qq": "https://qmsg.zendee.cn/send/",
        "tg": "https://dianbao.vercel.app/send/"
    }
} 
headers = {
    "User-Agent":
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.4",
    "Content-Type": "application/json"
}

class ClockIn():
    def __init__(self, args):
        self.info = {
            "xh": args.id,
            "xxdz": args.address,
            "openid": args.openid
        }
        self.flag = True

    def check_repeat(self):
        playload = {
            "xh": self.info["xh"],
            "timestamp": ulits.timestamp()
        }
        r = s.post(url=urls["get_mrdk"],
                   json={"key": ulits.base64_(playload)},
                   headers=headers,
                   timeout=1)
        if r.json()["data"]["count"] != "0":
            log.info("今天已打卡，本次打卡取消")
            return True
        else:
            return False

    def get_student_info(self):
        playload = {
            "openid": self.info["openid"],
            "key": self.info["xh"],
            "page": 1,
            "timestamp": ulits.timestamp()
        }
        r = s.post(url=urls["post_get_student"],
                   json={"key": ulits.base64_(playload)},
                   headers=headers,
                   timeout=1)
        if r.json()["data"]["total"]:
            data = r.json()["data"]["rows"][0]
            self.info["xb"] = data["xb"]
            self.info["name"] = data["xm"]
            log.info("学生信息获取成功")
        else:
            log.error("学号填写错误")
            self.flag = False

    def get_location_info(self):
        playload = {
            "address": self.info["xxdz"],
            #  请勿滥用，不然到时候谁也没得用
            "key": "PULBZ-BSEWU-MAEVV-2IAJR-ZCAS3-53F4O"
        }
        r = s.get(url=urls["get_location"], params=playload)
        if r.json()["status"] == 0:
            result = r.json()["result"]
            tmp = {
                "longitude": round(float(result["location"]['lng']) + random.uniform(0.0001, 0.00099), 6),
                "latitude": round(float(result["location"]['lat']) + random.uniform(0.0001, 0.00099), 6),
                "szdq": f"{result['address_components']['province']},{result['address_components']['city']},{result['address_components']['district']}",
                "locationSmall": result["address_components"]["city"] + result["address_components"]["district"] + result["title"],
                "locationBig": f"中国,{result['address_components']['province']},{result['address_components']['city']},{result['address_components']['district']}",
            }
            self.info.update(tmp)
            log.error("获取地理信息成功")
        else:
            log.error("地址查询失败，请参考地图填写")
            self.flag = False

    def clock_in(self):
        tmp = {
            #  // 新冠肺炎风险等级，非低风险地区请勿使用
            "ywjcqzbl": "低风险",
            #  // 14 天内是否有中高风险地区旅居史
            "ywjchblj": "无",
            #  // 14 天内是否接触过有中高风险地区旅居史的人员
            "xjzdywqzbl": "无",
            #  // 今日体温是否正常
            "twsfzc": "是",
            #  // 今日是否有与新冠病毒感染有关的症状
            "ywytdzz": "无",
            #  // 备注
            "beizhu": "无",
            "mrdkkey": ulits.mrdk_key(ulits.now.tm_mday, ulits.now.tm_hour),
            "timestamp": ulits.timestamp()
        }
        self.info.update(tmp)
        r = s.post(url=urls["post_mrdk"],
                   json={"key": ulits.base64_(self.info)},
                   headers=headers,
                   timeout=1)
        if r.json()["status"] == 200:
            log.info("自动打卡成功")
        else:
            log.error("自动打卡失败，请检查 openid 与学号是否对应")

    def run(self):
        # 如果没打卡
        try:
            if not self.check_repeat():
                self.get_student_info()
                self.get_location_info()
                if self.flag:
                    self.clock_in()
                else: 
                    log.error("自动打卡失败，请检查上述原因")
        except:
            log.error("自动打卡失败，无法连接服务器")

def send_notification(text):
    if ":" in text:
        type = text.split(":")[0].strip()
        if type not in ["tg","qq"]:
            log.error("推送不支持 "+type+"，请填写 tg 或 qq")
            return
        key = text.split(":")[1].strip()
    else:
        log.error("请正确填写推送信息")
        return
    with open("./all.log", 'r',encoding='utf-8') as logfile:
        logs = logfile.read()
    if type == "qq":
        s.get(url=urls["push"]["qq"]+key, params={"msg": logs.strip()}, timeout=1)
    else:
        s.get(url=urls["push"]["tg"]+key+"/"+quote(logs.strip()))

    
def main_handler(event, context):
    class Args():
        def __init__(self):
            pass
    args = Args()

    # 你的学号
    args.id = ""

    # 详细地址，建议精确到门牌号
    args.address = ""

    # 个人唯一的身份标示，与微信绑定，请自行抓包
    args.openid = ""

    # 推送，可以为空
    # 格式：qq:your key of qmsg 酱
    # 格式：tg:your key of tg 酱
    args.push = ""

    g = ClockIn(args)
    g.run()
    if args.push:
        send_notification(args.push)

if __name__ == '__main__':
    # 获取命令行传入的参数，暂时不需要
    # parser = argparse.ArgumentParser(
    #          description='''1）本脚本仅供学习交流使用，请勿过分依赖。时刻注意每天是否打卡成功，如若失败，请手动打卡。
    #  2）本脚本仅限低风险地区学生使用，并且不要前往中高风险地区。如果身体出现新冠肺炎相关症状，请立即报告辅导员。
    #  3）本脚本需要自行抓包才能正常使用，为了避免脚本被滥用，在此我不会提供抓包相关教程。抓包工具iOS推荐Stream，Android推荐HttpCanary。
    #  4）开发者对使用或不使用本脚本造成的问题不负任何责任，不对脚本执行效果做出任何担保，原则上不提供任何形式的技术支持。''')
    #      parser.add_argument('id', help='你的学号')
    #      parser.add_argument('address', help='详细地址，建议精确到门牌号')
    #      parser.add_argument('openid', help='个人唯一的身份标示，与微信绑定，请自行抓包')
    #      parser.add_argument('-p', '--push', help='推送到QQ 或者 Telegram')
    #      args = parser.parse_args()

    # 腾讯云入口函数
    main_handler('','')
