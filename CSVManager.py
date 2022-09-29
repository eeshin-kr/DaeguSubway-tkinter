import csv
import re
import tkinter.messagebox as msgbox
import time
import SettingsManager
import DownloadManager

## 업데이트 관련 함수는 제거됨
class CSVClass:
    csv_data = None
    current_line = None
    current_station_list =[]
    daytype_list = []
    col_idx_header = None
    col_idx_day = None
    col_idx_station = None

    def __init__(self, Line):
        self.set_line(Line)

    def set_line(self, Line):
        return self.load_file(Line)
                
    def load_file(self, Line):
        try:
            csv_file_name = SettingsManager.SettingsClass().load_timetable_file_name(Line)
            if csv_file_name == "":
                raise FileNotFoundError
            with open(f'./Cache/{csv_file_name}', 'r', encoding='euc-kr') as File: 
                self.csv_data = list(csv.reader(File))
            self.current_line = Line
            self.analyze_CSV()
            return 0
            
        except FileNotFoundError as Error:
            if msgbox.askyesno(title="열차 시간표 알리미",
                                           message=f'{Line}호선 시간표 파일을 찾을 수 없습니다. 다운로드 하시겠습니까?',
                                           icon = 'warning'):
                try_download = DownloadManager.download_from_json(Line)
                
                if try_download != 0:
                    if msgbox.askyesno(title="다운로드 중 오류가 발생했습니다.",message=try_download+"\n 재시도 하시겠습니까?",icon = 'error'):
                        self.load_file(Line)
                    return -1
                else:
                    return self.load_file(Line)
            return -1
            
        except:
            msgbox.showerror(title="CSV 파일을 읽는 도중 오류 발생", message="CSV 파일을 읽는 도중 오류가 발생하였습니다.")
            return -1
        
    def analyze_CSV(self):
        col_word_day = "요일별" #헤더 행 검색시 사용
        col_word_station="역명"  #헤더 행 검색시 사용
        sel_direction = "하"  #역사 리스트 작성 시 하선 기준 검색
        re_pattern_daytype = "\(.*\)"
        
        
        row_idx_header = None
        col_idx_day = None
        col_idx_station = None
        station_list = []
        daytype_list = []

        for row in self.csv_data:
            if col_word_station in row :  #헤더 행이 몇 행인지 확인
                row_idx_header = self.csv_data.index(row)
                col_idx_day = row.index(col_word_day)
                col_idx_station = row.index(col_word_station)
                break
  
        for row in self.csv_data[row_idx_header+1 : ]: #역사 리스트 추출
            if (sel_direction in row[col_idx_day]) :
                if row[col_idx_station] not in station_list:
                    station_list.append(row[col_idx_station])
                    
        for row in self.csv_data[row_idx_header+1 : ]: #사용 요일 추출
                daytype = re.sub(re_pattern_daytype,'',row[col_idx_day])
                if daytype not in daytype_list:
                    daytype_list.append(daytype)

        self.current_station_list = station_list
        self.daytype_list = daytype_list
        self.col_idx_header = row_idx_header
        self.col_idx_day = col_idx_day
        self.col_idx_station = col_idx_station


    def get_train_time_dict(self, DayType, Direction, Station):
        arrive_departure_type = "도착"
        train_time_dict = {}

        if Station not in self.current_station_list :
            raise NameError("검색하려는 역이 존재하지 않습니다.")

        for row in self.csv_data[self.col_idx_header + 1 : ] :
            if (DayType   in row[self.col_idx_day] and
                Direction in row[self.col_idx_day] and
                Station   in row):

                for col in row :
                    if(":" in col):
                        train_number = int(self.csv_data[self.col_idx_header][row.index(col)][-4:])
                        if arrive_departure_type in row :
                            train_time_dict[train_number] = col
                            
                        elif train_number not in train_time_dict.keys():
                            train_time_dict[train_number] = col

        return dict(sorted(train_time_dict.items()))
                
        
    def create_NowNextTrainClass(self, DayType, Direction, Station):
        
        train_dict = self.get_train_dict(DayType, Direction)
        train_dict_refined = {}
        for (train_number, train_time_list) in train_dict.items():

            arrive_time = train_time_list[self.current_station_list.index(Station)]
            if arrive_time == None:
                continue
            
            #열차 목적지 찾기 시작
            if Direction =="하": #하선일 경우 역순으로 찾아야 함
                tmplist = train_dict[train_number][::-1]
            else:
                tmplist = train_dict[train_number]
            
            for time_list in tmplist :
                if time_list != None :
                    tmp_time = time_list
                    break
                
            destination = self.current_station_list[train_dict[train_number].index(tmp_time)]
            #열차 목적지 찾기 끝

            arrive_time_sec = timestr_to_sec(arrive_time)
            train_dict_refined[train_number] = {"ArriveTime": arrive_time,
                                                "ArriveTimeSec" : arrive_time_sec,
                                                "Destination": destination}
            
        return self.NowNextTrainClass(train_dict_refined)

    class NowNextTrainClass:
        
        def __init__(self, TrainDict):
            self.train_dict = dict(sorted(TrainDict.items()))
            train_number_list = list(self.train_dict.keys())
            
            train_number_first = train_number_list[0]
            self.train_number_last = train_number_list[-1]
            self.train_number_first_sec = TrainDict[train_number_first]["ArriveTimeSec"]
            self.train_number_last_sec = TrainDict[self.train_number_last]["ArriveTimeSec"]
            
        def search_train_number(self, TargetTimeStr):
            target_time_sec = timestr_to_sec(TargetTimeStr)
            if target_time_sec < self.train_number_last_sec and  self.train_number_last_sec < self.train_number_first_sec :
                target_time_sec = target_time_sec + timestr_to_sec("24:00:00")
                
                
            for (train_number, value) in self.train_dict.items() :

                search_time_sec = value["ArriveTimeSec"]
                if value["ArriveTimeSec"] < self.train_number_first_sec :
                    search_time_sec = search_time_sec + timestr_to_sec("24:00:00")

                if search_time_sec > target_time_sec :
                    return train_number

            return -1
            
        def get_NowNextTrain(self):
            time_now = time.strftime("%H:%M:%S")
            train_number_now = self.search_train_number(time_now)

            if train_number_now == -1 :
                return [-1, -1]
            
            train_number_now_info = self.train_dict[train_number_now]
            train_number_now_info["TrainNumber"] = train_number_now
            
            if train_number_now == self.train_number_last :
                return [train_number_now_info , -1]
            
            train_number_next = self.search_train_number(train_number_now_info["ArriveTime"])
            train_number_next_info = self.train_dict[train_number_next]
            train_number_next_info["TrainNumber"] = train_number_next
            
            return [train_number_now_info, train_number_next_info]
   
    def get_train_dict(self, DayType, Direction):
        arrive_departure_type = "도착"
        station_idx_current = None
        train_number_dict = {}
        train_number_idx_dict = {}
        empty_list = [ None for a in range(len(self.current_station_list)) ] #역사 갯수 만큼의 None이 든 리스트
        each_list = [ None for a in range(len(self.current_station_list)) ] #한 열에 몇 개의 요소가 있는지 기록하는 리스트

        for col in self.csv_data[self.col_idx_header] :
            if col[-4:].isnumeric() :
                train_number = int(col[-4:])
                train_number_dict[train_number] = empty_list #열차 번호 - 시간대 리스트 저장
                train_number_idx_dict[self.csv_data[self.col_idx_header].index(col)] = train_number #인덱스 번호 - 열차 번호쌍 저장
                
        for row in self.csv_data[self.col_idx_header + 1: ] :            
            if (DayType in row[self.col_idx_day] and Direction in row[self.col_idx_day]):                
                station_idx_current = self.current_station_list.index(row[self.col_idx_station])

                #계산 양을 줄이기 위함, 한 열차가 해당 역에서 도착 또는 출발만 있는 경우 시간표 상에 도착과 출발
                #갯수가 차이난다. 차이가 나는 경우 해당 역사에는 출발 또는 도착만 있는 열차가 존재하므로 이 때는 연산을 진행한다.
                elements_occupied = len([el for el in row if el!="" ])
                if each_list[station_idx_current] == elements_occupied and arrive_departure_type not in row: 
                    continue
                each_list[station_idx_current] = elements_occupied
                
                for col in row :
                    if ":" in col:
                        train_number = train_number_idx_dict[row.index(col)]
                        tmp = list(train_number_dict[train_number])
                        tmp[station_idx_current] = col
                        if train_number_dict[train_number][station_idx_current] == None or (arrive_departure_type in row):
                            train_number_dict[train_number] = tmp
                            
        for (key, val) in list(train_number_dict.items()): #시간이 기록되지 않은 열차번호 제거
            if val == empty_list : del train_number_dict[key]

        return train_number_dict

    def get_station_list(self):
        return self.current_station_list
    
    def get_daytype_list(self):
        return self.daytype_list

    def get_train_destination(self, DayType, Direction, Station, TargetTime):
        train_dict = self.get_train_dict(DayType, Direction)
        station_dict_idx = self.current_station_list.index(Station)
        train_number_target = None
        tmp_time = None

        for (train_number, train_time) in train_dict.items():
            if TargetTime == train_time[station_dict_idx] :
                train_number_target = train_number
                break 

        if Direction =="하": #하선일 경우 역순으로 찾아야 함
            tmplist = train_dict[train_number_target][::-1]
        else:
            tmplist = train_dict[train_number_target]
        
        for time_list in tmplist :
            if time_list != None :
                tmp_time = time_list
                break

        destination = self.current_station_list[ train_dict[train_number_target].index(tmp_time) ]
        return destination
            

def timestr_to_sec(TStr):
    tmp_array = TStr.split(':')
    tmp_list = list(map(int,tmp_array))
    tmp_int = tmp_list[0] * 3600 + tmp_list[1] * 60 + tmp_list[2]
    return tmp_int


#a = CSVClass(2) 
#na = a.create_NowNextTrainClass("평일","상", "이곡")
#print(na.get_NowNextTrain())
#print(a.get_train_time_dict('평일', '상', '수성구청'))
#print(a.get_train_destination('평일', '하', '용산', '23:35:15'))

