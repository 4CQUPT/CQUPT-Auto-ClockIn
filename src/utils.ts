const dateCode = [
  "s9ZS",
  "jQkB",
  "RuQM",
  "O0_L",
  "Buxf",
  "LepV",
  "Ec6w",
  "zPLD",
  "eZry",
  "QjBF",
  "XPB0",
  "zlTr",
  "YDr2",
  "Mfdu",
  "HSoi",
  "frhT",
  "GOdB",
  "AEN0",
  "zX0T",
  "wJg1",
  "fCmn",
  "SM3z",
  "2U5I",
  "LI3u",
  "3rAY",
  "aoa4",
  "Jf9u",
  "M69T",
  "XCea",
  "63gc",
  "6_Kf"
]

const hourCode = [
  "89KC",
  "pzTS",
  "wgte",
  "29_3",
  "GpdG",
  "FDYl",
  "vsE9",
  "SPJk",
  "_buC",
  "GPHN",
  "OKax",
  "_Kk4",
  "hYxa",
  "1BC5",
  "oBk_",
  "JgUW",
  "0CPR",
  "jlEh",
  "gBGg",
  "frS6",
  "4ads",
  "Iwfk",
  "TCgR",
  "wbjP"
]

const getMrdkKey = (date = getLocalTime()) =>
  dateCode[date.getDate()] + hourCode[date.getHours()]

const Base64 = {
  decode(str: string) {},
  encode(str: string) {
    return Buffer.from(str).toString("base64")
  }
}

// 获取北京时间
const getLocalTime = () =>
  new Date(Date.now() + (new Date().getTimezoneOffset() + 8 * 60) * 60 * 1000)

// 获取当前时间戳
const getTimeStamp = () => Math.floor(Date.now() / 1000)

export { getLocalTime, getMrdkKey, getTimeStamp, Base64 }
