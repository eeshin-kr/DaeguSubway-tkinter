import time
import urllib.request
import urllib.parse
import json
import os


PublicAnniversaryURL = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
SetParams = {"serviceKey": "qwOsuA49e64sAt996zL7akPoB8B6xE8CyygnFiVOq24VOaz+vmR+usEwsayufqCPOc4wH5HhUaAqh/OqW6s7og==",
            "pageNo": 1,
            "numOfRows": 366,
            "solYear": 2022,
            "_type": "json"}
PAData = None

def DownloadData():
    global PAData
    global PublicAnniversaryURL
    global SetParams
    Thisyear = time.strftime("%Y")
    SetParams["solYear"] = Thisyear
    PAFilePath = "./Cache/"
    PAFileName = f'getRestDelInfoY{Thisyear}.json'
    PAFullFilePath = PAFilePath + PAFileName
    parameters = urllib.parse.urlencode(SetParams)
    try:
        with urllib.request.urlopen(url=PublicAnniversaryURL +"?"+ parameters) as response:
            response_text = response.read()
            PAData = json.loads(response_text)
            if PAData['response']['header']['resultCode'] != "00":
                raise NameError(JsonData['response']['header']['resultMsg'])
            if os.path.isdir(PAFilePath) == False :
                os.mkdir(PAFilePath)
            with open(PAFullFilePath, 'wb') as File:
                File.write(response_text)        

    except json.decoder.JSONDecodeError:
        raise NameError("JSON 다운로드 실패")
        
def LoadData():
    global PAData
    Thisyear = time.strftime("%Y")
    PAFilePath = "./Cache/"
    PAFileName = f'getRestDelInfoY{Thisyear}.json'
    PAFullFilePath = PAFilePath + PAFileName
    try: 
        with open(PAFullFilePath, 'r', encoding='UTF8') as File:
            PAFile = File.read()
        PAData = json.loads(PAFile)
        if PAData['response']['header']['resultCode'] != "00":
            raise FileNotFoundError

    except (FileNotFoundError, json.decoder.JSONDecodeError):
        DownloadData()


def GetTodayServiceDayPAData():
    global PAData
    if PAData == None :
        LoadData()
    NowDate = time.strftime("%Y%m%d")
    NowYear = time.strftime("%Y")
    DataYear = str(PAData['response']['body']['items']['item'][0]['locdate'])[:4]
    if DataYear != NowYear:
        LoadData()
    for el in PAData['response']['body']['items']['item']:
        if el['locdate'] == int(NowDate):
            return "휴일"
        
    
def GetTodayServiceDayLocal():
    Localwday = time.localtime().tm_wday
    if Localwday == 5 :
        return "토요일"
    elif Localwday == 6 :
        return "휴일"
    else:
        return "평일"


def GetTodayServiceDay():
    if GetTodayServiceDayLocal() == "휴일":
        return "휴일"
    elif GetTodayServiceDayPAData() == "휴일":
        return "휴일"
    else:
        return GetTodayServiceDayLocal()

