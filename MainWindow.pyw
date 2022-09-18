'''
메인 창을 나타내는 모듈입니다.
'''
import tkinter as tk
import time
import CSVManager
import GetDayType
import SettingsManager
import TimeTableWindow

Version = "0.5.3"
class MainWindow(tk.Tk):
    Title = "열차 시간 알리미"
    Settings = None
    CSV = None
    UpdateFrameID = None

    def __init__(self):
        super().__init__()
        self.Set_Window()
        self.Set_UI()
        self.Set_ProcessClassInit()
        self.Update_DayType()
        self.Update_UI_Label()
        self.Update_TrainInfo()

        
    def Set_Window(self):
        self.title (f'{self.Title}')
        self.resizable(False, False)
        #self.attributes("-toolwindow", True)

    def Set_UI(self):
        self.UIMenuBar = self.UIMenuBarClass(self)
        self.UIFrame = self.UIFrameClass(self)


    def Set_ProcessClassInit(self):
        self.Settings = SettingsManager.SettingsClass()
        self.CSV = CSVManager.CSVClass(self.Settings.LastLineLoad())
        self.CurrentLine = self.Settings.LastLineLoad()
        self.CurrentStation = self.Settings.LastStationLoad()
        self.StationList = self.CSV.GetStationList()
        self.CurrentDayType = self.CSV.GetDayTypeList()[0]

    def Update_DayType(self):
        '''
        휴일 여부를 받아오는 함수입니다.
        '''
        TodayType = GetDayType.GetTodayServiceDay()
        if TodayType in self.CSV.GetDayTypeList() :
            self.CurrentDayType = TodayType
        
        # 지금 시각과 24:00 사이의 초를 계산, 그 후 지정된 시간 만큼 초 더한 뒤 Millsec으로 변환
        NextLaunchTime = (TimeDiffInt("24:00:00")+SettingsManager.NextLaunchHour*3600) * 1000
        self.after(NextLaunchTime, self.Update_DayType)

    def Update_UI_Label(self):
        LineList = self.Settings.GetLineTotal()
        DayTypeList = self.CSV.GetDayTypeList()
        self.UIMenuBar.ChangeVar(self.CurrentLine, self.CurrentStation, self.CurrentDayType)
        self.UIMenuBar.ChangeLabel(LineList, self.StationList, DayTypeList)
        self.UIFrame.UpdateLabel([self.CurrentStation, self.CurrentDayType, self.StationList[0] ,self.StationList[-1] ])
    
    def Update_TrainInfo(self):
        TmpList = self.CSV.GetNowNextTrain(Direction = "상", Station = self.CurrentStation, DayType = self.CurrentDayType)
        TmpList2 = self.CSV.GetNowNextTrain(Direction = "하", Station = self.CurrentStation, DayType = self.CurrentDayType)
        TmpList3 = []
        TmpList4 = []
        TmpList5 = []
        for Tmp in TmpList + TmpList2 :
            if Tmp == -1 :
                TmpList3.append("-")
            else:
                TmpList3.append(Tmp[:-3])
        
        self.UIFrame.UpdateTime(TmpList3)


        for Tmp in TmpList:
            if Tmp != -1:
                Dest = self.CSV.GetTrainDestination(Direction = "상", Station = self.CurrentStation, DayType = self.CurrentDayType, TargetTime = Tmp)
                if Dest not in [self.StationList[0], self.StationList[-1]]:
                    TmpList4.append(Dest+" 행")
                    continue
            TmpList4.append(None)

        for Tmp in TmpList2:
            if Tmp != -1:
                Dest = self.CSV.GetTrainDestination(Direction = "하", Station = self.CurrentStation, DayType = self.CurrentDayType, TargetTime = Tmp)
                if Dest not in [self.StationList[0], self.StationList[-1]]:
                    TmpList4.append(Dest+" 행")
                    print("동작")
                    continue
            TmpList4.append(None)

        self.UIFrame.AddDestination(TmpList4)
                
        
        for Tmp in TmpList + TmpList2 :
            if Tmp == -1 :
                TmpList5.append("24:00:00")
            else:
                TmpList5.append(Tmp)
        
        LeftTimeList = list(map(TimeDiffInt, TmpList5))

        self.UpdateFrameID = self.after(min(LeftTimeList)*1000, self.Update_TrainInfo)

    def Cancel_Update_TrainInfo(self):
        self.after_cancel(self.UpdateFrameID)

    def Change_Settings(self):
        self.Cancel_Update_TrainInfo()
        if self.CurrentLine != self.UIMenuBar.GetVar()["Line"]: #호선 설정이 바뀌었을 때 작동
            
            if self.CSV.SetLine(self.UIMenuBar.GetVar()["Line"]) == -1: ## CSV 읽기에 실패했을 경우 탈출
                self.UIMenuBar.ChangeVar(self.CurrentLine, self.CurrentStation, self.CurrentDayType) #설정을 기본 설정으로 리셋
                return -1
            
            self.CurrentLine = self.UIMenuBar.GetVar()["Line"]
            self.CSV.SetLine(self.CurrentLine) #호선에 맞는 시간표 다시 읽기
            self.StationList = self.CSV.GetStationList()
            self.CurrentStation = self.StationList[0]
        else :
            self.CurrentStation = self.UIMenuBar.GetVar()["Station"]

        self.CurrentDayType = self.UIMenuBar.GetVar()["DayType"]
        self.Update_UI_Label()
        self.Update_TrainInfo()
        self.Settings.StationChangeSave(self.CurrentLine, self.CurrentStation)
        
    def Open_TimeTable(self):
        TimeTableWin = TimeTableWindow.TimeTableWindow(self, self.CurrentLine, self.CurrentStation, self.CurrentDayType)
        TimeTableWin.mainloop()


    def Open_HelpMsg(self):
        global Version
        MsgStr = f'공공데이터 포털 열차 시간표 기반의 표시 프로그램입니다.\n\n버전: {Version}\n만든이: realoven@gmail.com\n라이센스: GPL 3.0 '
        tk.messagebox.showinfo(title = "열차 시간 알리미 도움말", message = MsgStr)
        
        
    def Run(self):
        self.Set_ProcessClassInit()
        self.Update_DayType()
        self.Update_UI_Label()
        self.Update_TrainInfo()
        self.mainloop()
        
    class UIMenuBarClass(tk.Menu):
        tkmaster = None
    
        def __init__(self, master):
            super().__init__(master)
            self.tkmaster = master
            self.parent = master
            self.Create()

        def Create(self):      
            self.Menu_Tools = tk.Menu(master = self, tearoff = 0)
            self.Menu_Settings = tk.Menu(master = self, tearoff = 0)
            self.Menu_Lines = tk.Menu(master = self.Menu_Settings, tearoff = 0)        
            self.Menu_Stations = tk.Menu(master = self.Menu_Settings, tearoff = 0)
            self.Menu_DayType = tk.Menu(master = self.Menu_Settings, tearoff = 0)

            self.add_cascade(label="도구", menu = self.Menu_Tools)
            self.Menu_Tools.add_command(label="시간표 보기", command = self.CallTimeTable)
            
            
            self.add_cascade(label="설정", menu = self.Menu_Settings)
            self.Menu_Settings.add_cascade(label="호선 설정", menu = self.Menu_Lines)
            self.Menu_Settings.add_cascade(label="역 설정", menu = self.Menu_Stations)
            self.Menu_Settings.add_cascade(label="요일 설정", menu = self.Menu_DayType)
            self.add_command(label='도움말', command = self.CallHelpMsg)

            self.LinesVar = tk.IntVar()
            self.StationsVar = tk.StringVar()
            self.DayTypeVar = tk.StringVar()

            self.tkmaster.config(menu = self)            

        def ChangeLabel(self, LineList, StationList, DayTypeList):
            self.Menu_Lines.delete(0, 'end')
            self.Menu_Stations.delete(0, 'end')
            self.Menu_DayType.delete(0, 'end')
            for LineOption in LineList:
                self.Menu_Lines.add_radiobutton(label=f'{LineOption} 호선', variable=self.LinesVar, value = LineOption, command = self.CallChangeSettings)

            for StationOption in StationList:
                self.Menu_Stations.add_radiobutton(label=StationOption, variable=self.StationsVar, value = StationOption, command= self.CallChangeSettings)

            for DayTypeOption in DayTypeList:
                self.Menu_DayType.add_radiobutton(label=DayTypeOption, variable=self.DayTypeVar, value = DayTypeOption, command = self.CallChangeSettings)

        def CallChangeSettings(self):
            self.parent.Change_Settings()

        def CallTimeTable(self):
            self.parent.Open_TimeTable()

        def CallADCalWindow(self):
            self.parent.Open_ADCalWindow()

        def CallHelpMsg(self):
            self.parent.Open_HelpMsg()
        

        def ChangeVar(self, Line, Station, DayType):
            self.LinesVar.set(Line)
            self.StationsVar.set(Station)
            self.DayTypeVar.set(DayType)

        def GetVar(self):
            return {"Line": self.LinesVar.get(),
                    "Station": self.StationsVar.get(),
                    "DayType": self.DayTypeVar.get()}
            


    class UIFrameClass:
        master = None

        def __init__(self, master):
            self.master = master
            self.Create()
            
        def Create(self):
            #메인 프레임 구성
            self.MFrame = tk.LabelFrame(master = self.master, labelanchor="n", text=f'- / -')

            ##서브 프레임 구성
            self.SFrameTOP = tk.LabelFrame(master = self.MFrame, labelanchor = "n", text=f'- 방면')
            self.SFrameBOT = tk.LabelFrame(master = self.MFrame, labelanchor="n", text=f'- 방면')
            
            #시간 표시 프레임 구성
            self.TFrameTOP0 = tk.LabelFrame(master = self.SFrameTOP, labelanchor="n", text="이번 열차")
            self.TFrameTOP1 = tk.LabelFrame(master = self.SFrameTOP, labelanchor="n",text="다음 열차")
            self.TFrameBOT0 = tk.LabelFrame(master = self.SFrameBOT, labelanchor="n", text="이번 열차")
            self.TFrameBOT1 = tk.LabelFrame(master = self.SFrameBOT, labelanchor="n",text="다음 열차")

            #구성된 프레임 표시
            self.MFrame.pack(fill = tk.BOTH, expand = True)
            self.SFrameTOP.pack(fill=tk.BOTH, padx = 10, pady = 5, expand=True)
            self.SFrameBOT.pack(fill=tk.BOTH, padx = 10, pady = 5, expand=True)
            self.TFrameTOP0.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            self.TFrameTOP1.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            self.TFrameBOT0.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            self.TFrameBOT1.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            
            #라벨 구성
            TFrameList = [self.TFrameTOP0, self.TFrameTOP1, self.TFrameBOT0, self.TFrameBOT1]
            self.TTimeLabelList = []
            for frame in TFrameList:
                Tmp = self.UILabelClass(master = frame)
                Tmp.pack()
                self.TTimeLabelList.append(Tmp)

            
                
            self.TDestLabelList = []
            for frame in TFrameList:
                self.TDestLabelList.append(self.UILabelClass(master = frame))

            

        def UpdateLabel(self, Val):
            self.MFrame.config(text=f'{Val[0]} / {Val[1]}')
            self.SFrameTOP.config(text=f'{Val[2]} 방면')
            self.SFrameBOT.config(text=f'{Val[3]} 방면')
            

        def UpdateTime(self, Val):
            ZippedList = zip(self.TTimeLabelList, Val)
            for el, val in ZippedList:
                el.ChangeStr(val)


        def AddDestination(self, Val):
            ZippedList = zip(self.TDestLabelList, Val)
            for el, val in ZippedList:
                if val != None:
                    el.ChangeStr(val)
                    el.Visible()
                else:
                    el.Invisible()

        class UILabelClass(tk.Label):
            def __init__(self, master, string = "-"):
                super().__init__(master)
                self.LabelStringVar = tk.StringVar(value = string)
                self.config(textvariable=self.LabelStringVar)
                
            def ChangeStr(self, string):
                self.LabelStringVar.set(string)

            def Visible(self):
                self.pack()

            def Invisible(self):
                self.pack_forget()


def TimeStr_2_Sec(TStr):
    TmpArray = TStr.split(':')
    TmpList = list(map(int,TmpArray))
    TmpInt = TmpList[0] * 3600 + TmpList[1] * 60 + TmpList[2]
    return TmpInt

def TimeDiffInt(TimeStr):
    TimeNowInt = TimeStr_2_Sec(time.strftime("%H:%M:%S"))
    TimeDesInt = TimeStr_2_Sec(TimeStr)
    if TimeNowInt > TimeDesInt:
        return 24*3600 - TimeNowInt + TimeDesInt
    else:
        return TimeDesInt - TimeNowInt

        
a = MainWindow()
a.mainloop()
