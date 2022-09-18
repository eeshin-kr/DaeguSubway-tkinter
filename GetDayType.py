'''
외부에서 오늘이 평일/토요일/휴일인지 받아오기 위한 함수입니다.
'''
import time
import urllib.request
import urllib.error
import json

typeDict = {1: "평일",
            2: "토요일",
            3: "휴일"}

def GetTodayServiceDayNaver():
    '''
    모바일 네이버 지도에서 휴일 정보를 받아오는 함수입니다.
    '''
    CurrentTimeStr = time.strftime("%Y%m%d%H%M%S")
    NaverMapAPI = f'https://m.map.naver.com/pubtrans/getSubwayTimestamp.naver?inquiryDateTime={CurrentTimeStr}'
    req = urllib.request.Request(NaverMapAPI, data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
                                )
    
    try:
        with urllib.request.urlopen(req) as response:
            Encoding = response.info().get_content_charset()
            Data = response.read()
            
        jsonData = json.loads(Data.decode(Encoding))
        todayServiceDay = jsonData['result']['dateType']
        if todayServiceDay not in list(typeDict.keys()):
            raise NameError("DayType에 맞지 않는 현상 발생")
        return typeDict.get(todayServiceDay)

    except (urllib.error.HTTPError, NameError) as e:
         print(e)
         return -1
        
    except:
        return -1


def GetTodayServiceDayNaverPC():
    '''
    PC 네이버 지도에서 휴일 정보를 받아오는 함수입니다. 파일 용량이 모바일 네이버 지도에서 받는 정보 보다 큽니다.
    '''
    
    NaverMapAPI = "https://map.naver.com/v5/api/transit/subway/stations/40230/schedule?lang=ko&stationID=40230"
    req = urllib.request.Request(NaverMapAPI, data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
                                )
    try:
        with urllib.request.urlopen(NaverMapAPI) as response:
            Encoding = response.info().get_content_charset()
            Data = response.read()
            
        jsonData = json.loads(Data.decode(Encoding))
        todayServiceDay = jsonData['todayServiceDay']['name']

        return todayServiceDay
        
    except urllib.error.HTTPError as e:
        print(e.__dict__)
        return -1
    
    except:
        return -1

def GetTodayServiceDayLocal():
    Localwday = time.localtime().tm_wday
    if Localwday == 5 :
        return "토요일"
    elif Localwday == 6 :
        return "휴일"
    else:
        return "평일"

def GetTodayServiceDay():
    Localwday = GetTodayServiceDayLocal()
    if Localwday == "휴일":
        return Localwday
    else:
        Naverwday = GetTodayServiceDayNaver()
        if Naverwday != -1:
            return Naverwday
        NaverwdayPC = GetTodayServiceDayNaverPC()
        if NaverwdayPC != -1:
            return NaverwdayPC
    return Localwday
                    

