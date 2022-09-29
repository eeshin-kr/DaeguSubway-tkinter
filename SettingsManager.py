'''
설정 파일을 관리하는 모듈입니다.
'''
import configparser
import os

 #설정 파일명 설정
DIR_NAME = './Cache/'
FILE_NAME = 'Settings.ini'
FILE_PATH = DIR_NAME + FILE_NAME

#설정 파일 내부 설정
Section_Name_1 = 'Settings'
Section_Name_2 = 'DatabaseUpdateDate'
Section_Name_3 = 'DatabaseFileName'

#어느 모듈에서도 설정 값을 가져올 수 있는 MagicWord 설정
MAGICWORD_LINE = 'line'
MAGICWORD_STATION = 'station'
MAGICWORD_LINE1_DB = 'line1'
MAGICWORD_LINE2_DB = 'line2'
MAGICWORD_LINE3_DB = 'line3'

#호선별 SWITCH_CASE문을 사용하기 위한 딕셔너리 자료형입니다.
SETDBDATE_CASE = {1:MAGICWORD_LINE1_DB,
               2:MAGICWORD_LINE2_DB,
               3:MAGICWORD_LINE3_DB }

ConfigStyle = configparser.ConfigParser()

ConfigStyle[Section_Name_1] = {
    MAGICWORD_LINE: '2',
    MAGICWORD_STATION: '용산' }

ConfigStyle[Section_Name_2] = {
    MAGICWORD_LINE1_DB: '',
    MAGICWORD_LINE2_DB: '',
    MAGICWORD_LINE3_DB: '' }

ConfigStyle[Section_Name_3] = {
    MAGICWORD_LINE1_DB: '',
    MAGICWORD_LINE2_DB: '',
    MAGICWORD_LINE3_DB: '' }


class SettingsClass:
    config = None

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load_setting_file()

    def load_setting_file(self):        
        self.dataset = self.config.read(FILE_PATH)

        ### 메인 부분 파일이 존재하지 않을 때 설정 파일 생성
        if os.path.isdir(DIR_NAME) == False :
            os.mkdir(DIR_NAME)
            
        if FILE_PATH not in self.dataset :
            self.config = ConfigStyle
            self.save_to_file()
        

    def load_last_used_line(self) :

        return int(dict(self.config[Section_Name_1])[MAGICWORD_LINE])

    def load_last_used_station(self) :
        '''
        사용자의 호선 및 역 설정 값을 불러들이는 메소드입니다.
        '''
        return dict(self.config[Section_Name_1])[MAGICWORD_STATION]


    def save_station_setting(self,line, station) :
        '''
        사용자의 호선 및 역 설정 값을 저장하는 함수입니다.
        '''
        self.load_setting_file()
        self.config[Section_Name_1][MAGICWORD_LINE] = str(line)
        self.config[Section_Name_1][MAGICWORD_STATION] = station
        self.save_to_file()
        
    
    def load_timetable_file_update_date(self):
        '''
        저장된 시간표 파일의 정보에 관한 정보를 불러들이는 함수입니다.
        '''
        return dict(self.config[Section_Name_2])

    def load_timetable_file_name(self, line):
        '''
        저장된 시간표 파일의 정보를 불러들이는 함수입니다.
        '''
        return self.config[Section_Name_3][SETDBDATE_CASE[line]]
        

    def save_timetable_file_info(self, line, date, filename):
        '''
        저장한 시간표 파일의 정보를 설정파일에 기록하는 함수입니다.
        '''
        self.config[Section_Name_2][SETDBDATE_CASE[line]] = date
        self.config[Section_Name_3][SETDBDATE_CASE[line]] = filename
        self.save_to_file()

    def get_total_line(self):
        '''
        몇 호선이 기록되어 있는지 알아내기 위한 함수
        '''
        return list(SETDBDATE_CASE.keys())

    def save_to_file(self):
        with open(FILE_PATH, 'w') as File:
            self.config.write(File)
        

