import csv
import re
import tkinter.messagebox as msgbox
import time
import SettingsManager
import DownloadManager

## 업데이트 관련 함수는 제거됨
class CSVClass:
    CSVData = None
    CurrentLine = None
    CurrentStationList =[]
    DayTypeList = []
    CSVHeaderRowNum = None
    CSVDayColNum = None
    CSVStationColNum = None

    def __init__(self, Line):
        self.SetLine(Line)

    def SetLine(self, Line):
        return self.LoadFile(Line)
                
    def LoadFile(self, Line):
        try:
            CSVFileName = SettingsManager.SettingsClass().DatabaseFileNameLoad(Line)
            if CSVFileName == "":
                raise FileNotFoundError
            with open(f'./Cache/{CSVFileName}', 'r', encoding='euc-kr') as File: 
                self.CSVData = list(csv.reader(File))
            self.CurrentLine = Line
            self.AnalyzeCSV()
            return 0
            
        except FileNotFoundError as Error:
            if msgbox.askyesno(title="열차 시간표 알리미",
                                           message=f'{Line}호선 시간표 파일을 찾을 수 없습니다. 다운로드 하시겠습니까?',
                                           icon = 'warning'):
                TryDownload = DownloadManager.DownloadFromJson(Line)
                
                if TryDownload != 0:
                    if msgbox.askyesno(title="다운로드 중 오류가 발생했습니다.",message=TryDownload+"\n 재시도 하시겠습니까?",icon = 'error'):
                        self.LoadFile(Line)
                    return -1
                else:
                    return self.LoadFile(Line)
            return -1
            
        except:
            msgbox.showerror(title="CSV 파일을 읽는 도중 오류 발생", message="CSV 파일을 읽는 도중 오류가 발생하였습니다.")
            return -1
        
    def AnalyzeCSV(self):
        DayColWord = "요일별" #헤더 행 검색시 사용
        StColWord="역명"  #헤더 행 검색시 사용
        Direction = "하"  #역사 리스트 작성 시 하선 기준 검색
        DayTypeSubtractPattern = "\(.*\)"
        
        
        HeaderRow = None
        DayCol = None
        StationCol = None
        StationList = []
        DayTypeList = []

        for Row in self.CSVData:
            if StColWord in Row :  #헤더 행이 몇 행인지 확인
                HeaderRow = self.CSVData.index(Row)
                DayCol = Row.index(DayColWord)
                StationCol = Row.index(StColWord)
                break
  
        for Row in self.CSVData[HeaderRow+1 : ]: #역사 리스트 추출
            if (Direction in Row[DayCol]) :
                if Row[StationCol] not in StationList:
                    StationList.append(Row[StationCol])
                    
        for Row in self.CSVData[HeaderRow+1 : ]: #사용 요일 추출
                DayType = re.sub(DayTypeSubtractPattern,'',Row[DayCol])
                if DayType not in DayTypeList:
                    DayTypeList.append(DayType)

        self.CurrentStationList = StationList
        self.DayTypeList = DayTypeList
        self.CSVHeaderRowNum = HeaderRow
        self.CSVDayColNum = DayCol
        self.CSVStationColNum = StationCol


    def GetTrainTimeList(self, DayType, Direction, Station):
        AdType = "도착"
        TrainTimeList = []

        if Station not in self.CurrentStationList :
            raise NameError("검색하려는 역이 존재하지 않습니다.")

        if Station in [self.CurrentStationList[0], self.CurrentStationList[-1]] : #시점 및 시점일 때는 도착, 출발 정보가 하나 밖에 없으므로 AdType을 Station으로 바꾸어 AdType 조건을 회피한다.
            AdType = Station

        for Row in self.CSVData[self.CSVHeaderRowNum + 1 : ] :
            if (DayType   in Row[self.CSVDayColNum] and
                Direction in Row[self.CSVDayColNum] and
                Station   in Row                    and
                AdType    in Row):

                for Col in Row :
                    if(":" in Col):
                        TrainTimeList.append(Col)

                return TrainTimeList
        
    def CreateNowNextTrainClass(self, DayType, Direction, Station):
        
        TrainDict = self.GetTrainDict(DayType, Direction)
        rTrainDict = {}
        for (TrainNo, TrainTimeList) in TrainDict.items():

            ArriveTime = TrainTimeList[self.CurrentStationList.index(Station)]
            if ArriveTime == None:
                continue
            
            #열차 목적지 찾기 시작
            if Direction =="하": #하선일 경우 역순으로 찾아야 함
                tmplist = TrainDict[TrainNo][::-1]
            else:
                tmplist = TrainDict[TrainNo]
            
            for TimeList in tmplist :
                if TimeList != None :
                    TmpTime = TimeList
                    break
                
            Destination = self.CurrentStationList[TrainDict[TrainNo].index(TmpTime)]
            #열차 목적지 찾기 끝

            ArriveTimeSec = TimeStr_2_Sec(ArriveTime)
            rTrainDict[TrainNo] = {"ArriveTime": ArriveTime,
                                   "ArriveTimeSec" : ArriveTimeSec,
                                   "Destination": Destination}
            
        return self.NowNextTrainClass(rTrainDict)

    class NowNextTrainClass:
        
        def __init__(self, TrainDict):
            self.TrainDict = TrainDict
            TrainNoList = list(map(int, TrainDict.keys()))
            
            FirstTrainNumber = str(min(TrainNoList))
            self.LastTrainNumber = str(max(TrainNoList))
            self.FirstTrainTimeSec = TrainDict[FirstTrainNumber]["ArriveTimeSec"]
            self.LastTrainTimeSec = TrainDict[self.LastTrainNumber]["ArriveTimeSec"]
            
        def SearchTrainNo(self, TargetTimeStr):
            TargetTimeSec = TimeStr_2_Sec(TargetTimeStr)
            if TargetTimeSec < self.LastTrainTimeSec and  self.LastTrainTimeSec < self.FirstTrainTimeSec :
                TargetTimeSec = TargetTimeSec + TimeStr_2_Sec("24:00:00")
                
                
            for (TrainNo, Keys) in self.TrainDict.items() :

                SearchTimeSec = Keys["ArriveTimeSec"]
                if Keys["ArriveTimeSec"] < self.FirstTrainTimeSec :
                    SearchTimeSec = SearchTimeSec + TimeStr_2_Sec("24:00:00")

                if SearchTimeSec > TargetTimeSec :
                    return TrainNo

            return -1
            
        def GetNowNextTrain(self):
            NowTime = time.strftime("%H:%M:%S")
            NowTrainNo = self.SearchTrainNo(NowTime)

            if NowTrainNo == -1 :
                return [-1, -1]
            
            NowTrainInfo = self.TrainDict[NowTrainNo]
            NowTrainInfo["TrainNo"] = NowTrainNo
            
            if NowTrainNo == self.LastTrainNumber :
                return [NowTrainInfo , -1]
            
            NextTrainNo = self.SearchTrainNo(NowTrainInfo["ArriveTime"])
            NextTrainInfo = self.TrainDict[NextTrainNo]
            NextTrainInfo["TrainNo"] = NextTrainNo
            
            return [NowTrainInfo, NextTrainInfo]
   
    def GetTrainDict(self, DayType, Direction):
        AdType = "도착"
        CurrentStationIndex = None
        TrainNumDict = {}
        TrainNumIndexDict = {}
        EmptyList = [ None for a in range(len(self.CurrentStationList)) ] #역사 갯수 만큼의 None이 든 리스트
        SkipList = [ None for a in range(len(self.CurrentStationList)) ] # 출발, 도착을 했는지 기록하는 리스트

        for Col in self.CSVData[self.CSVHeaderRowNum] :
            if Col[-4:].isnumeric() :
                TrainNumDict[Col[-4:]] = EmptyList #열차 번호 - 시간대 리스트 저장
                TrainNumIndexDict[self.CSVData[0].index(Col)] = Col[-4:] #인덱스 번호 - 열차 번호쌍 저장

        for Row in self.CSVData[self.CSVHeaderRowNum + 1: ] :
            if (DayType in Row[self.CSVDayColNum] and Direction in Row[self.CSVDayColNum]):
                for Col in Row:
                    if Col in self.CurrentStationList:
                        #현재 검색중인 역사의 인덱스 번호 계산
                        CurrentStationIndex = self.CurrentStationList.index(Col)


                for Col in Row :
                    if SkipList[CurrentStationIndex] : break

                    if ":" in Col:
                        a = TrainNumIndexDict[Row.index(Col)]
                        tmp = list(TrainNumDict[a])
                        tmp[CurrentStationIndex] = Col
                        TrainNumDict[a] = tmp
                        
                if AdType in Row :
                    SkipList[CurrentStationIndex] = True
                        
        for (Key, Val) in list(TrainNumDict.items()): #시간이 기록되지 않은 열차번호 제거
            if Val == EmptyList : del TrainNumDict[Key]

        return TrainNumDict

    def GetStationList(self):
        return self.CurrentStationList
    
    def GetDayTypeList(self):
        return self.DayTypeList

##    def IsLastTrain(self, DayType, Direction, Station, TargetTime):
##        if self.GetTrainTimeList(DayType, Direction, Station)[-1] == TargetTime : return True
##        else: return False
##
    def GetTrainDestination(self, DayType, Direction, Station, TargetTime):
        TrainDict = self.GetTrainDict(DayType, Direction)
        DictStationIndex = self.CurrentStationList.index(Station)
        TargetTrainNo = None
        TmpTime = None
        TmpTime2 = None

        for (TrainNo, TrainTime) in TrainDict.items():
            if TargetTime == TrainTime[DictStationIndex] :
                TargetTrainNo = TrainNo
                break 

        if Direction =="하": #하선일 경우 역순으로 찾아야 함
            tmplist = TrainDict[TargetTrainNo][::-1]
        else:
            tmplist = TrainDict[TargetTrainNo]
        
        for TimeList in tmplist :
            if TimeList != None :
                TmpTime = TimeList
                break

        Destination = self.CurrentStationList[ TrainDict[TargetTrainNo].index(TmpTime) ]
        return Destination
            

def TimeStr_2_Sec(TStr):
    TmpArray = TStr.split(':')
    TmpList = list(map(int,TmpArray))
    TmpInt = TmpList[0] * 3600 + TmpList[1] * 60 + TmpList[2]
    return TmpInt


#a = CSVClass(2) 
#na = a.CreateNowNextTrainClass("평일","상", "이곡")
#print(na.GetNowNextTrain())
#print(a.GetNowNextTrain('평일', '하', '용산'))
#print(a.GetTrainDestination('평일', '하', '용산', '23:35:15'))

