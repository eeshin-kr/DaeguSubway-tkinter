import time
import urllib.request
import urllib.parse
import json
import os


URL_PUBLIC_ANNIVERSARY = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
DEFAULT_PARAMETERS = {"serviceKey": "qwOsuA49e64sAt996zL7akPoB8B6xE8CyygnFiVOq24VOaz+vmR+usEwsayufqCPOc4wH5HhUaAqh/OqW6s7og==",
                      "pageNo": 1,
                      "numOfRows": 366,
                      "solYear": 2022,
                      "_type": "json"}
PUBLIC_ANNIVERSARY_DATA = None

def DownloadData():
    global PUBLIC_ANNIVERSARY_DATA
    global DEFAULT_PARAMETERS
    now_year = time.strftime("%Y")
    DEFAULT_PARAMETERS["solYear"] = now_year
    PA_file_dir = "./Cache/"
    PA_file_name = f'getRestDelInfoY{now_year}.json'
    PA_file_path_full = PA_file_dir + PA_file_name
    parameters = urllib.parse.urlencode(DEFAULT_PARAMETERS)
    try:
        with urllib.request.urlopen(url=URL_PUBLIC_ANNIVERSARY +"?"+ parameters) as response:
            response_read = response.read()
            PUBLIC_ANNIVERSARY_DATA = json.loads(response_read)
            if PUBLIC_ANNIVERSARY_DATA['response']['header']['resultCode'] != "00":
                raise NameError(JsonData['response']['header']['resultMsg'])
            if os.path.isdir(PA_file_dir) == False :
                os.mkdir(PA_file_dir)
            with open(PA_file_path_full, 'wb') as File:
                File.write(response_read)        

    except json.decoder.JSONDecodeError:
        raise NameError("JSON 다운로드 실패")
        
def LoadData():
    global PUBLIC_ANNIVERSARY_DATA
    now_year = time.strftime("%Y")
    PA_file_dir = "./Cache/"
    PA_file_name = f'getRestDelInfoY{now_year}.json'
    PA_file_path_full = PA_file_dir + PA_file_name
    try: 
        with open(PA_file_path_full, 'r', encoding='UTF8') as File:
            PA_file_data = File.read()
        PUBLIC_ANNIVERSARY_DATA = json.loads(PA_file_data)
        if PUBLIC_ANNIVERSARY_DATA['response']['header']['resultCode'] != "00":
            raise FileNotFoundError

    except (FileNotFoundError, json.decoder.JSONDecodeError):
        DownloadData()


def GetTodayServiceDayPAData():
    global PUBLIC_ANNIVERSARY_DATA
    if PUBLIC_ANNIVERSARY_DATA == None :
        LoadData()
    now_date = time.strftime("%Y%m%d")
    now_year = time.strftime("%Y")
    data_year = str(PUBLIC_ANNIVERSARY_DATA['response']['body']['items']['item'][0]['locdate'])[:4]
    if data_year != now_year:
        LoadData()
    for el in PUBLIC_ANNIVERSARY_DATA['response']['body']['items']['item']:
        if el['locdate'] == int(now_date):
            return "휴일"
        
    
def GetTodayServiceDayLocal():
    now_weekday = time.localtime().tm_wday
    if now_weekday == 5 :
        return "토요일"
    elif now_weekday == 6 :
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

