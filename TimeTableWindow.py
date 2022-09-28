'''
시간표 창을 표시하기 위한 모듈입니다.
'''
import tkinter as tk
from tkinter import ttk
import CSVManager
import SettingsManager

TopWinLine = None
TopWinStation = None
TopWinDayType = None

class TimeTableWindow(tk.Toplevel):
    TimeTableWin = None
    Title="시간표"
    tkmaster = None

    def __init__(self, master, Line , Station, DayType):
        super().__init__(master)        
        self.tkmaster = master
        global TopWinLine
        global TopWinStation
        global TopWinDayType
        TopWinLine = Line
        TopWinStation = Station
        TopWinDayType = DayType
        
        self.Set_Window()
        Notebook = self.NotebookClass(self)

    def Set_Window(self):
        self.title (f'{self.Title}')
        self.geometry("600x500")
        #self.attributes("-toolwindow", True)

        
    class NotebookClass(ttk.Notebook): #시간표 탭 생성

        def __init__(self, master):
            super().__init__(master)
            self.tkmaster = master
            self.pack(fill = tk.BOTH, expand=True, pady=2)
            self.Draw_Main_UI()

        def Draw_Main_UI(self):
            self.page1 = self.Frame1(self)
            self.page2 = self.Frame2(self)
            self.add(self.page1, text="역사별 시간표")
            self.add(self.page2, text="열차별 시간표")
            
            
            

        class Frame1(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                parent = master
                self.Set_ProcessClassInit()
                self.DrawUI()
                self.UpdateTable()
                

            def Set_ProcessClassInit(self):
                global TopWinLine
                global TopWinStation
                global TopWinDayType
                self.line = TopWinLine
                self.station = TopWinStation
                self.daytype = TopWinDayType
                self.CSV = CSVManager.CSVClass(self.line)
                self.station_list = self.CSV.GetStationList()
                self.daytype_list = self.CSV.GetDayTypeList()
                self.var_selection_line = tk.IntVar(value = self.line)
                self.var_selection_line_2 = tk.IntVar(value = self.line)
                self.var_selection_station = tk.StringVar(value = self.station) 
                self.var_selection_daytype = tk.StringVar(value = self.daytype)
                self.var_left_train_first = tk.StringVar(value = "-")
                self.var_left_train_last = tk.StringVar(value = "- (-행)")
                self.var_left_train_last_2 = tk.StringVar(value = "- (-행)")
                self.var_right_train_first = tk.StringVar(value = "-")
                self.var_right_train_last = tk.StringVar(value = "- (-행)")
                self.var_right_train_last_2 = tk.StringVar(value = "- (-행)")

            def DrawUI(self):
                self.TFrame0 = tk.LabelFrame(master = self, labelanchor="n", text="호선 설정")
                self.TFrame1 = tk.LabelFrame(master = self, labelanchor="n", text="역 설정")
                self.TFrame2 = tk.LabelFrame(master = self, labelanchor="n", text="휴일 설정")
                self.TFrame3 = tk.LabelFrame(master = self, labelanchor="n", text=f'{self.station_list[0]} 방면')
                self.TFrame4 = tk.LabelFrame(master = self, labelanchor="n", text=f'{self.station_list[-1]} 방면')
                self.TFrame5 = tk.Frame(master= self.TFrame3)
                self.TFrame6 = tk.Frame(master= self.TFrame4)
                
                self.TSpinBox = ttk.Spinbox(master = self.TFrame0, from_ = SettingsManager.SettingsClass().GetLineTotal()[0],
                                            to= SettingsManager.SettingsClass().GetLineTotal()[-1],
                                            textvariable = self.var_selection_line_2, command = self.ChangeLine)
                self.TComboBox = ttk.Combobox(master = self.TFrame1, textvariable = self.var_selection_station)
                self.TComboBox['values'] = self.station_list
                
                for txt in self.daytype_list:           
                    self.TRadioButton = tk.Radiobutton(master=self.TFrame2, text=txt, variable=self.var_selection_daytype, value=txt, command= self.UpdateTable)
                    self.TRadioButton.pack(fill=tk.X, side=tk.LEFT, expand=True)


                self.T_LEFT_FirstTrainCaption = tk.Label(master=self.TFrame5, anchor="w", text = "첫차:")
                self.T_LEFT_FirstTrain = tk.Label(master = self.TFrame5, anchor="w", textvariable = self.var_left_train_first)
                self.T_LEFT_LastTrainCaption = tk.Label(master=self.TFrame5, anchor="w", text = "막차:")
                self.T_LEFT_LastTrain = tk.Label(master = self.TFrame5, anchor="w", textvariable = self.var_left_train_last)
                self.T_LEFT_LastTrain_2 = tk.Label(master = self.TFrame5, anchor="w", textvariable = self.var_left_train_last_2)
                
                self.T_RIGHT_FirstTrainCatpion = tk.Label(master=self.TFrame6, anchor="w", text = "첫차:")
                self.T_RIGHT_FirstTrain = tk.Label(master = self.TFrame6, anchor="w", textvariable = self.var_right_train_first)
                self.T_RIGHT_LastTrainCaption = tk.Label(master=self.TFrame6, anchor="w", text = "막차:")
                self.T_RIGHT_LastTrain = tk.Label(master=self.TFrame6, anchor="w", textvariable = self.var_right_train_last)
                self.T_RIGHT_LastTrain_2 = tk.Label(master=self.TFrame6, anchor="w", textvariable = self.var_right_train_last_2)
                
                
                self.TFrame0.pack(fill=tk.X, expand=False)
                self.TFrame1.pack(fill=tk.X, expand=False)
                self.TFrame2.pack(fill=tk.X, expand=False)
                self.TFrame3.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
                self.TFrame4.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)
                self.TFrame5.pack(fill=tk.X)
                self.TFrame6.pack(fill=tk.X)
                self.TSpinBox.pack(fill=tk.X, expand=True, padx = 2, pady = 2)
                self.TSpinBox.bind('<Return>', lambda e: self.ChangeLine())
                self.TComboBox.pack(fill=tk.X, expand=True, padx = 2, pady = 2)
                self.TComboBox.bind('<<ComboboxSelected>>', lambda e: self.UpdateTable())
                self.TComboBox.bind('<Return>', lambda e: self.UpdateTable())

                self.TFrame5.columnconfigure(1, weight=1)
                self.TFrame5.columnconfigure(2, weight=1)
                self.T_LEFT_FirstTrainCaption.grid(row = 0, column = 0)
                self.T_LEFT_FirstTrain.grid(row = 0, column = 1, columnspan = 2)
                self.T_LEFT_LastTrainCaption.grid(row = 1, column = 0)
                self.T_LEFT_LastTrain.grid(row = 1, column = 1, sticky="e")
                self.T_LEFT_LastTrain_2.grid(row = 1, column = 2, sticky="w")
                
                self.TFrame6.columnconfigure(1, weight=1)
                self.TFrame6.columnconfigure(2, weight=1)
                self.T_RIGHT_FirstTrainCatpion.grid(row = 0, column = 0)
                self.T_RIGHT_FirstTrain.grid(row = 0, column = 1, columnspan = 2)
                self.T_RIGHT_LastTrainCaption.grid(row = 1, column = 0)
                self.T_RIGHT_LastTrain.grid(row = 1, column = 1, sticky="e")
                self.T_RIGHT_LastTrain_2.grid(row = 1, column = 2, sticky="w")
                
                
                
                self.T_LEFT_ListBox = tk.Listbox(master=self.TFrame3, selectmode="browse")
                self.T_RIGHT_ListBox = tk.Listbox(master=self.TFrame4, selectmode="browse")
                self.T_LEFT_ScrollBar = tk.Scrollbar(master = self.TFrame3)
                self.T_RIGHT_ScrollBar = tk.Scrollbar(master = self.TFrame4)
                
                self.T_LEFT_ListBox.config(yscrollcommand = self.T_LEFT_ScrollBar.set)
                self.T_RIGHT_ListBox.config(yscrollcommand = self.T_RIGHT_ScrollBar.set)
                self.T_LEFT_ScrollBar.config(command = self.T_LEFT_ListBox.yview)
                self.T_RIGHT_ScrollBar.config(command = self.T_RIGHT_ListBox.yview)

                self.T_LEFT_ListBox.pack(fill=tk.BOTH, side=tk.LEFT, pady=5 ,expand=True)
                self.T_RIGHT_ListBox.pack(fill=tk.BOTH, side=tk.LEFT, pady=5 ,expand=True)
                self.T_LEFT_ScrollBar.pack(fill = tk.Y, side=tk.LEFT, padx=2, pady=5, expand=False)
                self.T_RIGHT_ScrollBar.pack(fill = tk.Y, side=tk.LEFT, padx=2, pady=5, expand=False)


            def UpdateTable(self):
                self.T_LEFT_ListBox.delete(0, tk.END) #리스트 박스 초기화
                self.T_RIGHT_ListBox.delete(0, tk.END)

                timetable_list_left = self.CSV.GetStationTimeDict(DayType = self.var_selection_daytype.get(),
                                                                  Direction="상",
                                                                  Station= self.var_selection_station.get())
                
                timetable_list_right = self.CSV.GetStationTimeDict(DayType = self.var_selection_daytype.get(),
                                                                   Direction="하",
                                                                   Station= self.var_selection_station.get())

                for (train_number, train_time)  in list(timetable_list_left.items())[:-2] :
                    self.T_LEFT_ListBox.insert(tk.END, f'{train_number} | {train_time[:-3]}')

                for (train_number, train_time)  in list(timetable_list_left.items())[-2:]  :
                    Dest = self.CSV.GetTrainDestination(Direction = "상", Station = self.var_selection_station.get(), DayType = self.var_selection_daytype.get(), TargetTime = train_time)
                    self.T_LEFT_ListBox.insert(tk.END, f'{train_number} | {train_time[:-3]} ({Dest} 행)')

                for (train_number, train_time)  in list(timetable_list_right.items())[:-2] :
                    self.T_RIGHT_ListBox.insert(tk.END, f'{train_number} | {train_time[:-3]}')
                    
                for (train_number, train_time)  in list(timetable_list_right.items())[-2:]  :
                    Dest = self.CSV.GetTrainDestination(Direction = "하", Station = self.var_selection_station.get(), DayType = self.var_selection_daytype.get(), TargetTime = train_time)
                    self.T_RIGHT_ListBox.insert(tk.END, f'{train_number} | {train_time[:-3]} ({Dest} 행)')

                self.var_left_train_first.set(f'{self.T_LEFT_ListBox.get(0)}')
                self.var_left_train_last.set(f'{self.T_LEFT_ListBox.get(self.T_LEFT_ListBox.size()-2)}')
                self.var_left_train_last_2.set(f'{self.T_LEFT_ListBox.get(self.T_LEFT_ListBox.size()-1)}')

                self.var_right_train_first.set(f'{self.T_RIGHT_ListBox.get(0)}')
                self.var_right_train_last.set(f'{self.T_RIGHT_ListBox.get(self.T_RIGHT_ListBox.size()-2)}')
                self.var_right_train_last_2.set(f'{self.T_RIGHT_ListBox.get(self.T_RIGHT_ListBox.size()-1)}')

                
            def ChangeLine(self):
                if self.CSV.SetLine(self.var_selection_line_2.get()) == -1:
                    self.var_selection_line_2.set(self.var_selection_line.get())
                    return -1
                self.var_selection_line.set(self.var_selection_line_2.get())
                self.station_list = self.CSV.GetStationList()
                self.var_selection_station.set(self.station_list[0])
                self.TComboBox['values'] = self.station_list
                self.TFrame3.config(text=f'{self.station_list[0]} 방면')
                self.TFrame4.config(text=f'{self.station_list[-1]} 방면')
                self.UpdateTable()

        class Frame2(tk.Frame):

            def __init__(self, master):
                super().__init__(master)
                self.Set_ProcessClassInit()
                self.DrawUI()
                self.UpdateTreeView()

            def Set_ProcessClassInit(self):
                global TopWinLine
                global TopWinDayType
                self.CSV = CSVManager.CSVClass(TopWinLine)
                self.station_list = self.CSV.GetStationList()
                self.daytype_list = self.CSV.GetDayTypeList()
                self.var_selection_line = tk.IntVar(value = TopWinLine)
                self.var_selection_line_2 = tk.IntVar(value = TopWinLine)
                self.var_selection_direction = tk.StringVar(value = "상")
                self.var_selection_daytype = tk.StringVar(value = TopWinDayType)

            def DrawUI(self):
                self.columnconfigure(1, weight=1)
                self.rowconfigure(0,weight=1)
                self.OptionFrame = tk.Frame(master = self)
                self.OptionFrame.grid(row = 0, column = 0, sticky = "sn")
                self.TFrame0 = tk.LabelFrame(master = self.OptionFrame, text="호선", labelanchor="n")
                self.TFrame1 = tk.LabelFrame(master = self.OptionFrame, text="상/하선", labelanchor="n")
                self.TFrame2 = tk.LabelFrame(master = self.OptionFrame, text="휴일", labelanchor="n")
            
                self.TSpinBox = ttk.Spinbox(master = self.TFrame0, from_ = SettingsManager.SettingsClass().GetLineTotal()[0],
                            to= SettingsManager.SettingsClass().GetLineTotal()[-1],
                            textvariable = self.var_selection_line_2, command = self.ChangeLine)

                self.TRadioButtonGroup0 = []
                self.TRadioButtonGroup0.append( tk.Radiobutton(master = self.TFrame1, text = f'{self.station_list[0]} 방면',
                                                   variable = self.var_selection_direction, value = "상", command = self.UpdateTreeView)
                                                )
                
                self.TRadioButtonGroup0.append( tk.Radiobutton(master = self.TFrame1, text = f'{self.station_list[-1]} 방면',
                                                   variable = self.var_selection_direction, value = "하", command = self.UpdateTreeView)
                                                )
                
                self.TRadioButtonGroup0[0].pack(side=tk.TOP, anchor="w")
                self.TRadioButtonGroup0[1].pack(side=tk.TOP, anchor="w")
                        

                for daytype in self.daytype_list:
                    TRadioButton1 = tk.Radiobutton(master = self.TFrame2, text=daytype, variable = self.var_selection_daytype, value=daytype, command = self.UpdateTreeView)
                    TRadioButton1.pack(side=tk.TOP, anchor="w")

                self.TreeView = ttk.Treeview(master = self)
                self.TreeView['show'] = 'headings'
                

                ScrollBarX = tk.Scrollbar(master = self, orient = tk.HORIZONTAL)
                ScrollBarY = tk.Scrollbar(master = self, orient = tk.VERTICAL)

                SizeGrip = ttk.Sizegrip(master = self)
                
                self.TreeView.config(xscrollcommand = ScrollBarX.set, yscrollcommand = ScrollBarY.set)
                ScrollBarX.config(command=self.TreeView.xview)
                ScrollBarY.config(command=self.TreeView.yview)

                self.TFrame0.pack(fill=tk.BOTH)
                self.TFrame1.pack(fill=tk.BOTH)
                self.TFrame2.pack(fill=tk.BOTH)
                self.TSpinBox.pack(fill=tk.BOTH, padx = 2, pady = 2)
                self.TreeView.grid(row=0, column=1, sticky="nswe")
                ScrollBarX.grid(row = 1, column = 1, sticky = "ew")
                ScrollBarY.grid(row = 0, column = 2, sticky = "sn")
                SizeGrip.grid(row=1, column=2, sticky=tk.SE)

            def UpdateTreeView(self):
                self.TreeView.delete(*self.TreeView.get_children()) #Treeview 내용 제거

                if self.var_selection_direction.get() == "상":
                    self.TreeView['columns'] = ['열차번호'] + self.station_list[::-1]
                else :
                    self.TreeView['columns'] = ['열차번호'] + self.station_list
                
                for col in self.TreeView['columns']:
                    self.TreeView.column(col, anchor=tk.CENTER, width=60, stretch=False) 
                    self.TreeView.heading( col, text=col, anchor=tk.CENTER)

                TrainDict = self.CSV.GetTrainDict(DayType = self.var_selection_daytype.get(),
                                                  Direction = self.var_selection_direction.get())


                for key, val in TrainDict.items():
                    newlist = [key]
                    newlist2=[]
                    for el in val: #분까지만 표시
                        if el != None:
                            newlist2.append(el[:-3])
                        else:
                            newlist2.append(None)
                        
                    if self.var_selection_direction.get() == "상" :
                        newlist.extend(newlist2[::-1])
                    else:
                        newlist.extend(newlist2)
                        
                    self.TreeView.insert(parent='', index='end', iid=key, values=newlist)


            def ChangeLine(self):
                if self.CSV.SetLine(self.var_selection_line_2.get()) == -1:
                    self.var_selection_line_2.set(self.var_selection_line.get())
                    return -1
                self.var_selection_line.set(self.var_selection_line_2.get())
                self.station_list = self.CSV.GetStationList()
                self.TRadioButtonGroup0[0].config(text = f'{self.station_list[0]} 방면')
                self.TRadioButtonGroup0[1].config(text = f'{self.station_list[-1]} 방면')                    
                self.UpdateTreeView()


                
#a = TimeTableWindow(master = tk.Tk(), line = 2, station="대실", DayType ="평일")
#a.mainloop()
