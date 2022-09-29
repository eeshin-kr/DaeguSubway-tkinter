'''
시간표(Database)를 외부 사이트에서 가져오기 위한 함수입니다.
'''
import urllib.request
import urllib.error
import json
import os
import SettingsManager

#호선별 시간표 정보 JSON 다운로드 주소입니다.
Line1 = "https://www.data.go.kr/catalog/15065526/fileData.json"
Line2 = "https://www.data.go.kr/catalog/3033376/fileData.json"
Line3 = "https://www.data.go.kr/catalog/15065532/fileData.json"
#SWITCH_CASE문 처럼 사용하기 위한 딕셔너리 변수입니다.
JSON_CASE = {1: Line1,
            2: Line2,
            3: Line3}



def get_timetable_last_date(LineNum):
    '''
    시간표(Database)의 최신 수정일자(Date)를 받아오기 위한 함수입니다.
    '''
    try:
        json_url = JSON_CASE[LineNum]
        json_open = urllib.request.urlopen(url=json_url)
        json_open_read = json_open.read()
        json_encoding = json_open.info().get_content_charset()
        json_data = json.loads(json_open_read.decode(json_encoding))
        date_last_modified = json_data['dateModified']

        return date_last_modified
    except TimeoutError as e:
        print("타임아웃 에러 발생")
        return -1
    except urllib.error.URLError as e:
        print("URL 에러 발생")
        return -1
              
        



def download_from_json(LineNum):
    '''
    JSON 파일로 부터 시간표 파일을 받아오기 위한 함수입니다.
    '''
    try:
        json_url = JSON_CASE[LineNum]
        json_open = urllib.request.urlopen(url=json_url)
        json_open_read = json_open.read()
        json_encoding = json_open.info().get_content_charset()
        json_data = json.loads(json_open_read.decode(json_encoding))

        distribution_data = json_data['distribution']
        distribution_dict = dict(distribution_data[0])
        csv_download_url = distribution_dict['contentUrl']

        csv_download_open = urllib.request.urlopen(url=csv_download_url)
        csv_download_data = csv_download_open.read()
        if LineNum == 2 :
            csv_download_data = fix_CSV(csv_download_data)
        #파일 이름 가져오기
        csv_download_file_name_raw = csv_download_open.headers.get_filename()
        csv_download_file_name = csv_download_file_name_raw.encode('ISO-8859-1').decode('utf-8') #파일 이름이 ISO-8859-1로 인코딩 되어 있음...
        if os.path.isdir('./Cache') == False :
            os.mkdir('./Cache')
        #파일 저장하기
        with open(f'./Cache/{csv_download_file_name}', mode="wb") as file:
            file.write(csv_download_data)
        #설정파일에 파일 수정일 및 파일명 저장
        SettingsManager.SettingsClass().save_timetable_file_info(line = LineNum, date = get_timetable_last_date(LineNum), filename=csv_download_file_name)
        return 0

    except (TimeoutError, urllib.error.URLError) as e:
        return e

    
    
##2호선에 신매역이 신내역으로 기록, 이름 수정함
def fix_CSV(CSV_Byte):
    '''
    외부의 CSV 파일에 문제가 있을 경우 CSV파일을 수정하기 위해 사용하는 함수입니다.
    '''
    CSV_Byte = CSV_Byte.decode('euc-kr')
    CSV_Byte = CSV_Byte.replace("신내","신매") #2호선 파일에 신매역이 신내역으로 기록되어 있음
    return CSV_Byte.encode('euc-kr')

def check_timetable_update(LineNum):
    '''
    설정 파일의 수정일과 외부 파일의 수정일을 비교하여 업데이트가 필요한지 확인하는 함수입니다.
    '''
    LastDBD = get_timetable_last_date(LineNum)
    SavedDBD = SettingsManager.SettingsClass().load_timetable_file_update_date()[SettingsManager.SETDBDATE_CASE[LineNum]]
    if LastDBD == -1 :
        return -1
    elif LastDBD != SavedDBD :
        return [SavedDBD, LastDBD]
    else:
        return False
    


