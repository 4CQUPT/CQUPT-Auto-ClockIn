import { Base64, getMrdkKey, getTimeStamp } from "utils"
import got from "got"
import { option } from "option"
import {
  ClockInOption,
  QmsgOption,
  QQMapResponseByAddress,
  QQMapResponseByLocation
} from "types"

const gotOption = {
  headers: {
    "User-Agent":
      "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.4"
  },
  timeout: {
    request: 3000
  },
  retry: {
    limit: 5
  }
}

class ClockIn {
  private openid: string
  private id: string
  private address: string
  constructor(option: ClockInOption) {
    this.openid = option.openid
    this.id = option.id
    this.address = option.address
  }
  async getStudentInfo(id: string) {
    try {
      const res = (await got
        .get(
          "https://be-prod.redrock.cqupt.edu.cn/magipoke-text/search/people",
          {
            ...gotOption,
            searchParams: {
              stu: id
            }
          }
        )
        .json()) as {
        status: number | 200
        data: {
          name: string
          gender: string
        }[]
      }
      if (res.status !== 200 || res.data.length === 0) throw "获取个人信息失败"
      return {
        name: res.data[0].name,
        xb: res.data[0].gender
      }
    } catch (err) {
      console.log(err)
      return {
        name: undefined,
        xb: undefined
      }
    }
  }
  async getLocation(address: string) {
    try {
      // 第一次先获取坐标
      const res1 = (await got
        .get("https://apis.map.qq.com/ws/geocoder/v1", {
          ...gotOption,
          searchParams: {
            address,
            // We 重邮使用的 key
            key: "7IMBZ-XWMWW-D4FR5-R3NAG-G7A7S-FMBFN"
          }
        })
        .json()) as QQMapResponseByAddress
      if (res1.status !== 0) throw res1.message
      const { lng, lat } = res1.result.location
      const res2 = (await got
        .get("https://apis.map.qq.com/ws/geocoder/v1", {
          ...gotOption,
          searchParams: {
            location: `${lat},${lng}`,
            key: "7IMBZ-XWMWW-D4FR5-R3NAG-G7A7S-FMBFN"
          }
        })
        .json()) as QQMapResponseByLocation
      if (res2.status !== 0) throw res2.message
      return {
        latitude: res2.result.location.lat,
        longitude: res2.result.location.lng,
        locationBig: res2.result.ad_info.name,
        locationSmall: res2.result.address,
        szdq: res2.result.ad_info.name.slice(3)
      }
    } catch (err) {
      console.log(err)
      return {
        latitude: undefined,
        longitude: undefined,
        locationBig: undefined,
        locationSmall: undefined,
        szdq: undefined
      }
    }
  }
  async go() {
    const info = {
      openid: this.openid,
      xh: this.id,
      // // 详细地址
      xxdz: this.address,
      ...(await this.getStudentInfo(this.id)),
      ...(await this.getLocation(this.address)),
      mrdkkey: getMrdkKey(),
      timestamp: getTimeStamp(),

      // 新冠肺炎风险等级，非低风险地区请勿使用
      ywjcqzbl: "低风险",
      // 14 天内是否有中高风险地区旅居史
      ywjchblj: "无",
      // 14 天内是否接触过有中高风险地区旅居史的人员
      xjzdywqzbl: "无",
      // 今日体温是否正常
      twsfzc: "是",
      // 今日是否有与新冠病毒感染有关的症状
      ywytdzz: "无",
      beizhu: "无"
    }

    if (Object.values(info).some(val => val === undefined)) {
      console.log("打卡失败")
      return false
    }
    try {
      const res = (await got
        .post("https://we.cqupt.edu.cn/api/mrdk/post_mrdk_info.php", {
          ...gotOption,
          json: {
            key: Base64.encode(JSON.stringify(info))
          }
        })
        .json()) as {
        status: 200 | number
      }
      if (res.status !== 200) throw "打卡失败"
      return true
    } catch (err) {
      console.log(err)
      return false
    }
  }
}

const checkClocked = async (id: string) => {
  try {
    const res = (await got
      .post("https://we.cqupt.edu.cn/api/mrdk/get_mrdk_flag.php", {
        ...gotOption,
        json: {
          key: Base64.encode(
            JSON.stringify({
              xh: id,
              timestamp: getTimeStamp()
            })
          )
        }
      })
      .json()) as {
      status: number
      data: {
        count: "0" | "1"
      }
    }
    if (res.status !== 200) throw "打卡查询失败，稍后重试"
    if (res.data.count == "0") return false
    else return true
  } catch (err) {
    console.log(err)
    return undefined
  }
}
const push = async (msg: string, option: QmsgOption) => {
  try {
    const res = (await got
      .post(`https://qmsg.zendee.cn/send/${option.token}`, {
        ...gotOption,
        form: {
          msg,
          qq: option.qq
        }
      })
      .json()) as {
      success: boolean
      reason: string
    }
    if (!res.success) throw res.reason
  } catch (err) {
    console.log(err)
  }
}

// 腾讯云入口函数
export const main_handler = async (event?: any, context?: any) => {
  const isClocked = await checkClocked(option.clockIn.id)
  if (isClocked === undefined || isClocked) {
    await push(isClocked ? "请不要重复打卡" : "检查打卡失败", option.qmsg)
    return
  }
  const clockIn = new ClockIn(option.clockIn)
  const isSuccess = await clockIn.go()
  await push(isSuccess ? "打卡成功" : "打卡失败，请自行检查", option.qmsg)
}

// 测试使用
// main_handler()
