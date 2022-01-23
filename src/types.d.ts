export type ClockInOption = {
  openid: string
  id: string
  address: string
}
export type QmsgOption = {
  qq: string
  token: string
}
export type Option = {
  clockIn: ClockInOption
  qmsg: QmsgOption
}

export type QQMapResponseByAddress = {
  status: 0 | number
  message: "query ok" | string
  result: {
    title: string
    location: { lng: number; lat: number }
    ad_info: { adcode: string }
    address_components: {
      province: string
      city: string
      district: string
      street: string
      street_number: string
    }
    // 相似度，小数 < 1
    similarity: number
    deviation: number
    reliability: number
    level: number
  }
}

export type QQMapResponseByLocation = {
  status: 0 | number
  message: "query ok" | string
  result: {
    location: { lat: number; lng: number }
    // small
    address: string
    ad_info: {
      // big
      name: string
    }
  }
}
