'''
메인 창을 나타내는 모듈입니다.
'''
import tkinter as tk
import time
import CSVManager
import GetDayType
import SettingsManager
import TimeTableWindow

NEXT_UPDATE_DAYTYPE_TIME = "01:00:00"
Version = "0.5.6"
class MainWindow(tk.Tk):
    Title = "열차 시간 알리미"
    settings = None
    CSV = None
    after_id_traininfo = None
    after_id_lefttime = None

    def __init__(self):
        super().__init__()
        self.set_window()
        self.Set_UI()
        self.set_vars()
        self.update_daytype()
        self.update_train_time()

        
    def set_window(self):
        self.title (f'{self.Title}')
        self.resizable(False, False)
        self.attributes("-toolwindow", True)

    def Set_UI(self):
        self.UI_menu_bar = self.UIMenuBarClass(self)
        self.UI_frame = self.UIFrameClass(self)


    def set_vars(self):
        self.settings = SettingsManager.SettingsClass()
        self.CSV = CSVManager.CSVClass(self.settings.load_last_used_line())
        self.current_line = self.settings.load_last_used_line()
        self.current_station = self.settings.load_last_used_station()
        self.current_station_list = self.CSV.get_station_list()
        self.current_daytype = self.CSV.get_daytype_list()[0]
        self.option_show_time_left = False
        self.option_show_train_number = False
        self.set_now_next_train_class()

    def set_now_next_train_class(self):
        self.CSV_NowNextTrain_Class_UP = self.CSV.create_NowNextTrainClass(self.current_daytype, "상", self.current_station)
        self.CSV_NowNextTrain_Class_DOWN = self.CSV.create_NowNextTrainClass(self.current_daytype, "하", self.current_station)
        

    def update_daytype(self):
        '''
        휴일 여부를 받아오는 함수입니다.
        '''
        current_daytype = GetDayType.get_today_service_day()
        if current_daytype in self.CSV.get_daytype_list() :
            self.current_daytype = current_daytype
            
        
        # 지금 시각과 24:00 사이의 초를 계산, 그 후 지정된 시간 만큼 초 더한 뒤 Millsec으로 변환
        next_launch_time = (get_time_diff_from_now("24:00:00")+timestr_to_sec(NEXT_UPDATE_DAYTYPE_TIME)) * 1000
        self.update_UI_label()#UI 라벨, 값 업데이트
        self.set_now_next_train_class()
        self.after(next_launch_time, self.update_daytype)

    def update_UI_label(self):
        line_list = self.settings.get_total_line()
        daytype_list = self.CSV.get_daytype_list()
        self.UI_menu_bar.ChangeLabel(line_list, self.current_station_list, daytype_list)
        self.UI_menu_bar.ChangeVar(self.current_line, self.current_station, self.current_daytype)
        self.UI_frame.update_main_label([self.current_station, self.current_daytype, self.current_station_list[0] ,self.current_station_list[-1] ])
        

    def update_train_time(self):

        tmplist0 = []
        tmplist1 = []
        tmplist2 = []

        self.UP_NowNextTrain_dict = self.CSV_NowNextTrain_Class_UP.get_NowNextTrain()
        self.DOWN_NowNextTrain_dict=self.CSV_NowNextTrain_Class_DOWN.get_NowNextTrain()
        
        for val in self.UP_NowNextTrain_dict + self.DOWN_NowNextTrain_dict :
            if val == -1 :
                tmplist0.append("-") #열차 시각을 표시
                tmplist1.append(None) #행선지 표시, 막차일 경우 표시하지 않음
                tmplist2.append("24:00:00") #다음 업데이트 시간 계산용도
            else:
                tmplist0.append(val["ArriveTime"][:-3])
                tmplist2.append(val["ArriveTime"])
                #행선지 표시
                if val["Destination"] in [self.current_station_list[0], self.current_station_list[-1]]:
                    tmplist1.append(None)# 행선지가 시점/종점일 경우 표시하지 않음
                else:
                    tmplist1.append(val["Destination"]+" 행")#행선지가 시점/종점이 아닐 경우 표시


        self.UI_frame.update_time_label(tmplist0)
        self.UI_frame.update_destination_label(tmplist1)
                
        time_left_list = list(map(get_time_diff_from_now, tmplist2))
        time_after = min(time_left_list) * 1000
        self.after_id_traininfo = self.after(time_after, self.update_train_time)

    def set_always_on_top(self):
        if self.UI_menu_bar.GetVar()["Option_always_on_top"] == True:
            self.attributes('-topmost', True)
            self.update()
        else:
            self.attributes('-topmost', False)
            self.update()
            

    def refresh_options(self):
        if self.option_show_time_left == True:
            self.cancel_update_train_timeleft()
            self.update_train_timeleft()

        if self.option_show_train_number == True:
            self.cancel_update_train_number()
            self.update_train_number()

    def change_options(self):
        menu_settings_dict = self.UI_menu_bar.GetVar()
        if self.option_show_time_left != menu_settings_dict["Option_TimeLeft"]:
            self.option_show_time_left = menu_settings_dict["Option_TimeLeft"]
            if self.option_show_time_left == True:
                self.update_train_timeleft()
            elif self.option_show_time_left == False :
                self.cancel_update_train_timeleft()
                self.UI_frame.update_timeleft_label([None for a in range(4)])

        if self.option_show_train_number != menu_settings_dict["Option_TrainNo"]:
            self.option_show_train_number = menu_settings_dict["Option_TrainNo"]
            if self.option_show_train_number == True:
                self.update_train_number()
            elif self.option_show_train_number == False:
                self.cancel_update_train_number()
                self.UI_frame.update_train_number_label([None for a in range(4)])
                

        
    def update_train_number(self):
        tmplist0 = []
        tmplist1 = []
        
        for val in self.UP_NowNextTrain_dict + self.DOWN_NowNextTrain_dict :
            if val == -1:
                tmplist0.append("-")
                tmplist1.append("24:00:00")
            else:
                tmplist0.append(val["TrainNumber"])
                tmplist1.append(val["ArriveTime"])

        time_left_list = list(map(get_time_diff_from_now, tmplist1))
        time_after = min(time_left_list) * 1000

        self.UI_frame.update_train_number_label(tmplist0)
        self.after_id_train_number = self.after(time_after, self.update_train_number)
        

    def update_train_timeleft(self):
        tmplist0 = []

        for val in self.UP_NowNextTrain_dict + self.DOWN_NowNextTrain_dict :
            if val == -1 :
                tmplist0.append("-")
            else:
                tmp_time = get_time_diff_from_now(val["ArriveTime"])
                tmplist0.append(f'{tmp_time//60}m {tmp_time%60}s')

        self.UI_frame.update_timeleft_label(tmplist0)
        self.after_id_lefttime = self.after(1000, self.update_train_timeleft)


    def cancel_update_train_number(self):
        if self.after_id_train_number != None:
            self.after_cancel(self.after_id_train_number)
        
    def cancel_update_train_timeleft(self):
        if self.after_id_lefttime != None:
            self.after_cancel(self.after_id_lefttime)
        
    def cancel_update_train_time(self):
        self.after_cancel(self.after_id_traininfo)

    def change_settings(self):
        self.cancel_update_train_time()
        if self.current_line != self.UI_menu_bar.GetVar()["Line"]: #호선 설정이 바뀌었을 때 작동
            
            if self.CSV.set_line(self.UI_menu_bar.GetVar()["Line"]) == -1: ## CSV 읽기에 실패했을 경우 탈출
                self.UI_menu_bar.ChangeVar(self.current_line, self.current_station, self.current_daytype) #설정을 기본 설정으로 리셋
                return -1
            
            self.current_line = self.UI_menu_bar.GetVar()["Line"]
            self.CSV.set_line(self.current_line) #호선에 맞는 시간표 다시 읽기
            self.current_station_list = self.CSV.get_station_list()
            self.current_station = self.current_station_list[0]
        else :
            self.current_station = self.UI_menu_bar.GetVar()["Station"]
            
        self.current_daytype = self.UI_menu_bar.GetVar()["DayType"]
        self.CSV_NowNextTrain_Class_UP = self.CSV.create_NowNextTrainClass(self.current_daytype, "상", self.current_station)
        self.CSV_NowNextTrain_Class_DOWN = self.CSV.create_NowNextTrainClass(self.current_daytype, "하", self.current_station)
        self.update_UI_label()
        self.update_train_time()
        self.refresh_options()
        self.settings.save_station_setting(self.current_line, self.current_station)
        
    def open_timetable_window(self):
        TimeTableWin = TimeTableWindow.TimeTableWindow(self, self.current_line, self.current_station, self.current_daytype)
        TimeTableWin.mainloop()

    def open_help_msg(self):
        global Version
        msgstr = f'공공데이터 포털 열차 시간표 기반 표시 프로그램\n\n버전: {Version}\n만든이: realoven@gmail.com\n라이센스: GPL 3.0 '
        tk.messagebox.showinfo(title = "열차 시간 알리미 도움말", message = msgstr)
        
    class UIMenuBarClass(tk.Menu):
        tkmaster = None
    
        def __init__(self, master):
            super().__init__(master)
            self.tkmaster = master
            self.parent = master
            self.create()

        def create(self):

            self.var_lines = tk.IntVar()
            self.var_stations = tk.StringVar()
            self.var_daytype = tk.StringVar()
            self.option_show_timeleft = tk.BooleanVar(value=False)
            self.option_always_on_top = tk.BooleanVar(value=self.parent.attributes("-topmost"))
            self.option_show_train_number = tk.BooleanVar(value=False)
            

            self.menu_tools = tk.Menu(master = self, tearoff = 0)
            self.menu_settings = tk.Menu(master = self, tearoff = 0)
            self.menu_lines = tk.Menu(master = self.menu_settings, tearoff = 0)        
            self.menu_stations = tk.Menu(master = self.menu_settings, tearoff = 0)
            self.menu_daytype = tk.Menu(master = self.menu_settings, tearoff = 0)

            self.add_command(label="시간표 보기", command = self.CallTimeTable)
            
            self.add_cascade(label="설정", menu = self.menu_settings)
            self.menu_settings.add_cascade(label="호선 설정", menu = self.menu_lines)
            self.menu_settings.add_cascade(label="역 설정", menu = self.menu_stations)
            self.menu_settings.add_cascade(label="요일 설정", menu = self.menu_daytype)
            self.menu_settings.add_separator()
            self.menu_settings.add_checkbutton(label="열차번호 표시", variable = self.option_show_train_number, command = self.CallUpdateTrainNo)
            self.menu_settings.add_checkbutton(label="남은 시간 표시", variable = self.option_show_timeleft, command = self.CallUpdateLeftTime)
            self.menu_settings.add_checkbutton(label="창을 항상 위에 표시", variable = self.option_always_on_top, command = self.CallSetAlawaysOnTop)
            self.add_command(label='도움말', command = self.CallHelpMsg)

            self.tkmaster.config(menu = self)            

        def ChangeLabel(self, LineList, StationList, DayTypeList):
            self.menu_lines.delete(0, 'end')
            self.menu_stations.delete(0, 'end')
            self.menu_daytype.delete(0, 'end')
            for line_ in LineList:
                self.menu_lines.add_radiobutton(label=f'{line_} 호선', variable=self.var_lines, value = line_, command = self.CallChangeSettings)

            for station_ in StationList:
                self.menu_stations.add_radiobutton(label=station_, variable=self.var_stations, value = station_, command= self.CallChangeSettings)

            for daytype_ in DayTypeList:
                self.menu_daytype.add_radiobutton(label=daytype_, variable=self.var_daytype, value = daytype_, command = self.CallChangeSettings)

        def CallChangeSettings(self):
            self.parent.change_settings()

        def CallTimeTable(self):
            self.parent.open_timetable_window()

        def CallADCalWindow(self):
            self.parent.Open_ADCalWindow()

        def CallUpdateTrainNo(self):
            self.parent.change_options()

        def CallUpdateLeftTime(self):
            self.parent.change_options()

        def CallHelpMsg(self):
            self.parent.open_help_msg()
        
        def CallSetAlawaysOnTop(self):
            self.parent.set_always_on_top()
            
        def ChangeVar(self, Line, Station, DayType):
            self.var_lines.set(Line)
            self.var_stations.set(Station)
            self.var_daytype.set(DayType)

        def GetVar(self):
            return {"Line": self.var_lines.get(),
                    "Station": self.var_stations.get(),
                    "DayType": self.var_daytype.get(),
                    "Option_TimeLeft": self.option_show_timeleft.get(),
                    "Option_always_on_top": self.option_always_on_top.get(),
                    "Option_TrainNo": self.option_show_train_number.get()}
            


    class UIFrameClass:
        master = None

        def __init__(self, master):
            self.master = master
            self.create()
            
        def create(self):
            #메인 프레임 구성
            self.Main_Frame = tk.LabelFrame(master = self.master, labelanchor="n", text=f'- / -')

            ##서브 프레임 구성
            self.SubFrame_TOP = tk.LabelFrame(master = self.Main_Frame, labelanchor = "n", text=f'- 방면')
            self.SubFrame_BOT = tk.LabelFrame(master = self.Main_Frame, labelanchor="n", text=f'- 방면')
            
            #시간 표시 프레임 구성
            self.TimeFrame_TOP0 = tk.LabelFrame(master = self.SubFrame_TOP, labelanchor="n", text="이번 열차")
            self.TimeFrame_TOP1 = tk.LabelFrame(master = self.SubFrame_TOP, labelanchor="n",text="다음 열차")
            self.TimeFrame_BOT0 = tk.LabelFrame(master = self.SubFrame_BOT, labelanchor="n", text="이번 열차")
            self.TimeFrame_BOT1 = tk.LabelFrame(master = self.SubFrame_BOT, labelanchor="n",text="다음 열차")

            #구성된 프레임 표시
            self.Main_Frame.pack(fill = tk.BOTH, expand = True)
            self.SubFrame_TOP.pack(fill=tk.BOTH, padx = 10, pady = 5, expand=True)
            self.SubFrame_BOT.pack(fill=tk.BOTH, padx = 10, pady = 5, expand=True)
            self.TimeFrame_TOP0.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            self.TimeFrame_TOP1.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            self.TimeFrame_BOT0.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            self.TimeFrame_BOT1.pack(fill=tk.BOTH, padx = 5, pady = 5, expand=True, side=tk.LEFT)
            
            #라벨 구성
            time_frame_list = [self.TimeFrame_TOP0, self.TimeFrame_TOP1, self.TimeFrame_BOT0, self.TimeFrame_BOT1]
            for frame in time_frame_list:
                frame.columnconfigure(0, weight=1)
                frame.columnconfigure(1, weight=1)
                frame.columnconfigure(2, weight=1)
                
                
            
            self.train_number_label_list = []
            for frame in time_frame_list:
                self.train_number_label_list.append(self.UILabelClass(master=frame, gridrow = 0, gridcol = 1))
                
            
            self.train_time_label_list = []
            for frame in time_frame_list:
                Tmp = self.UILabelClass(master = frame, gridrow = 1, gridcol = 1)
                Tmp.visible()
                self.train_time_label_list.append(Tmp)

                
            self.train_destination_label_list = []
            for frame in time_frame_list:
                self.train_destination_label_list.append(self.UILabelClass(master = frame, gridrow = 2, gridcol = 1))


            self.train_timeleft_label_list = []
            for frame in time_frame_list:
                self.train_timeleft_label_list.append(self.UILabelClass(master = frame, gridrow = 3, gridcol = 1))
            

        def update_main_label(self, Val):
            self.Main_Frame.config(text=f'{Val[0]} / {Val[1]}')
            self.SubFrame_TOP.config(text=f'{Val[2]} 방면')
            self.SubFrame_BOT.config(text=f'{Val[3]} 방면')
            

        def update_time_label(self, Val):
            zipped_list = zip(self.train_time_label_list, Val)
            for el, val in zipped_list:
                el.change_str(val)


        def update_destination_label(self, Val):
            zipped_list = zip(self.train_destination_label_list, Val)
            for el, val in zipped_list:
                if val != None:
                    el.change_str(val)
                    el.visible()
                else:
                    el.invisible()
            
                    
        def update_timeleft_label(self, Val):
            zipped_list = zip(self.train_timeleft_label_list, Val)
            for (el, val) in zipped_list:
                if val != None:
                    el.change_str(val)
                    el.visible()
                else:
                    el.invisible()

        def update_train_number_label(self, Val):
            zipped_list = zip(self.train_number_label_list, Val)
            for (el, val) in zipped_list:
                if val != None:
                    el.change_str(val)
                    el.visible()
                else:
                    el.invisible()


                

        class UILabelClass(tk.Label):
            def __init__(self, master, gridrow, gridcol, string = "-"):
                super().__init__(master)
                self.var_label_string = tk.StringVar(value = string)
                self.config(textvariable=self.var_label_string)
                self.row = gridrow
                self.col = gridcol
                
            def change_str(self, string):
                self.var_label_string.set(string)

            def visible(self):
                self.grid(row=self.row, column = self.col, sticky="nswe")

            def invisible(self):
                self.grid_forget()


def timestr_to_sec(TStr):
    tmp_array = TStr.split(':')
    tmp_list = list(map(int,tmp_array))
    tmp_int = tmp_list[0] * 3600 + tmp_list[1] * 60 + tmp_list[2]
    return tmp_int

def get_time_diff_from_now(TimeStr):
    time_now_int = timestr_to_sec(time.strftime("%H:%M:%S"))
    time_destination_int = timestr_to_sec(TimeStr)
    if time_now_int > time_destination_int:
        return 24*3600 - time_now_int + time_destination_int
    else:
        return time_destination_int - time_now_int

        
a = MainWindow()
a.mainloop()

