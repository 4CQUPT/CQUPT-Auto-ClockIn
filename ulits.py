import base64
import json
import time
import logging
from logging import handlers

now = time.gmtime(time.time()+8 * 60 * 60 * 1000)

dateCode = [
    "s9ZS", "jQkB", "RuQM", "O0_L", "Buxf", "LepV", "Ec6w", "zPLD", "eZry",
    "QjBF", "XPB0", "zlTr", "YDr2", "Mfdu", "HSoi", "frhT", "GOdB", "AEN0",
    "zX0T", "wJg1", "fCmn", "SM3z", "2U5I", "LI3u", "3rAY", "aoa4", "Jf9u",
    "M69T", "XCea", "63gc", "6_Kf"
]
hourCode = [
    "89KC", "pzTS", "wgte", "29_3", "GpdG", "FDYl", "vsE9", "SPJk", "_buC",
    "GPHN", "OKax", "_Kk4", "hYxa", "1BC5", "oBk_", "JgUW", "0CPR", "jlEh",
    "gBGg", "frS6", "4ads", "Iwfk", "TCgR", "wbjP"
]
def timestamp():
    return int(time.time())

def base64_(data):
    return base64.b64encode(json.dumps(data).encode("utf-8")).decode()

def mrdk_key(d, h):
    return dateCode[d] + hourCode[h]


class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    } # 日志级别关系映射

    def __init__(self,filename,level='info'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter('%(asctime)s %(message)s','%H:%M:%S') # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level)) # 设置日志级别
        sh = logging.StreamHandler() # 往屏幕上输出
        sh.setFormatter(format_str) # 设置屏幕上显示的格式
        th = logging.FileHandler(filename=filename) # 输出到文件
        th.setFormatter(format_str) # 设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)
