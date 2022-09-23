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
            self.Page1 = self.Frame1(self)
            self.Page2 = self.Frame2(self)
            self.add(self.Page1, text="역사별 시간표")
            self.add(self.Page2, text="열차별 시간표")
            
            
            

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
                self.Line = TopWinLine
                self.Station = TopWinStation
                self.DayType = TopWinDayType
                self.CSV = CSVManager.CSVClass(self.Line)
                self.StationList = self.CSV.GetStationList()
                self.DayTypeList = self.CSV.GetDayTypeList()
                self.TLineSelection = tk.IntVar(value = self.Line)
                self.TLineSelection2 = tk.IntVar(value = self.Line)
                self.TStationSelection = tk.StringVar(value = self.Station) 
                self.TDayTypeSelection = tk.StringVar(value = self.DayType)
                self.TFirstTrainLEFTVar = tk.StringVar(value = "-")
                self.TLastTrainLEFTVar = tk.StringVar(value = "- (-행)")
                self.TLastTrainLEFTVar2 = tk.StringVar(value = "- (-행)")
                self.TFirstTrainRIGHTVar = tk.StringVar(value = "-")
                self.TLastTrainRIGHTVar = tk.StringVar(value = "- (-행)")
                self.TLastTrainRIGHTVar2 = tk.StringVar(value = "- (-행)")

            def DrawUI(self):
                self.TFrame0 = tk.LabelFrame(master = self, labelanchor="n", text="호선 설정")
                self.TFrame1 = tk.LabelFrame(master = self, labelanchor="n", text="역 설정")
                self.TFrame2 = tk.LabelFrame(master = self, labelanchor="n", text="휴일 설정")
                self.TFrame3 = tk.LabelFrame(master = self, labelanchor="n", text=f'{self.StationList[0]} 방면')
                self.TFrame4 = tk.LabelFrame(master = self, labelanchor="n", text=f'{self.StationList[-1]} 방면')
                self.TFrame5 = tk.Frame(master= self.TFrame3)
                self.TFrame6 = tk.Frame(master= self.TFrame4)
                
                self.TSpinBox = ttk.Spinbox(master = self.TFrame0, from_ = SettingsManager.SettingsClass().GetLineTotal()[0],
                                            to= SettingsManager.SettingsClass().GetLineTotal()[-1],
                                            textvariable = self.TLineSelection2, command = self.ChangeLine)
                self.TComboBox = ttk.Combobox(master = self.TFrame1, textvariable = self.TStationSelection)
                self.TComboBox['values'] = self.StationList
                
                for txt in self.DayTypeList:           
                    self.TRadioButton = tk.Radiobutton(master=self.TFrame2, text=txt, variable=self.TDayTypeSelection, value=txt, command= self.UpdateTable)
                    self.TRadioButton.pack(fill=tk.X, side=tk.LEFT, expand=True)


                self.TFirstTrainLEFTCap = tk.Label(master=self.TFrame5, anchor="w", text = "첫차:")
                self.TFirstTrainLEFT = tk.Label(master = self.TFrame5, anchor="w", textvariable = self.TFirstTrainLEFTVar)
                self.TLastTrainLEFTCap = tk.Label(master=self.TFrame5, anchor="w", text = "막차:")
                self.TLastTrainLEFT = tk.Label(master = self.TFrame5, anchor="w", textvariable = self.TLastTrainLEFTVar)
                self.TLastTrainLEFT2 = tk.Label(master = self.TFrame5, anchor="w", textvariable = self.TLastTrainLEFTVar2)
                
                self.TFirstTrainRIGHTCap = tk.Label(master=self.TFrame6, anchor="w", text = "첫차:")
                self.TFirstTrainRIGHT = tk.Label(master = self.TFrame6, anchor="w", textvariable = self.TFirstTrainRIGHTVar)
                self.TLastTrainRIGHTCap = tk.Label(master=self.TFrame6, anchor="w", text = "막차:")
                self.TLastTrainRIGHT = tk.Label(master=self.TFrame6, anchor="w", textvariable = self.TLastTrainRIGHTVar)
                self.TLastTrainRIGHT2 = tk.Label(master=self.TFrame6, anchor="w", textvariable = self.TLastTrainRIGHTVar2)
                
                
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
                self.TFirstTrainLEFTCap.grid(row = 0, column = 0)
                self.TFirstTrainLEFT.grid(row = 0, column = 1, columnspan = 2)
                self.TLastTrainLEFTCap.grid(row = 1, column = 0)
                self.TLastTrainLEFT.grid(row = 1, column = 1, sticky="e")
                self.TLastTrainLEFT2.grid(row = 1, column = 2, sticky="w")
                
                self.TFrame6.columnconfigure(1, weight=1)
                self.TFrame6.columnconfigure(2, weight=1)
                self.TFirstTrainRIGHTCap.grid(row = 0, column = 0)
                self.TFirstTrainRIGHT.grid(row = 0, column = 1, columnspan = 2)
                self.TLastTrainRIGHTCap.grid(row = 1, column = 0)
                self.TLastTrainRIGHT.grid(row = 1, column = 1, sticky="e")
                self.TLastTrainRIGHT2.grid(row = 1, column = 2, sticky="w")
                
                
                
                self.TListBoxLEFT = tk.Listbox(master=self.TFrame3, selectmode="browse")
                self.TListBoxRIGHT = tk.Listbox(master=self.TFrame4, selectmode="browse")
                self.TScrollBarLEFT = tk.Scrollbar(master = self.TFrame3)
                self.TScrollBarRIGHT = tk.Scrollbar(master = self.TFrame4)
                
                self.TListBoxLEFT.config(yscrollcommand = self.TScrollBarLEFT.set)
                self.TListBoxRIGHT.config(yscrollcommand = self.TScrollBarRIGHT.set)
                self.TScrollBarLEFT.config(command = self.TListBoxLEFT.yview)
                self.TScrollBarRIGHT.config(command = self.TListBoxRIGHT.yview)

                self.TListBoxLEFT.pack(fill=tk.BOTH, side=tk.LEFT, pady=5 ,expand=True)
                self.TListBoxRIGHT.pack(fill=tk.BOTH, side=tk.LEFT, pady=5 ,expand=True)
                self.TScrollBarLEFT.pack(fill = tk.Y, side=tk.LEFT, padx=2, pady=5, expand=False)
                self.TScrollBarRIGHT.pack(fill = tk.Y, side=tk.LEFT, padx=2, pady=5, expand=False)


            def UpdateTable(self):
                self.TListBoxLEFT.delete(0, tk.END) #리스트 박스 초기화
                self.TListBoxRIGHT.delete(0, tk.END)

                TimeTableContentLEFT = self.CSV.GetTrainTimeList(DayType = self.TDayTypeSelection.get(),
                                                            Direction="상",
                                                            Station= self.TStationSelection.get())
                
                TimeTableContentRIGHT = self.CSV.GetTrainTimeList(DayType = self.TDayTypeSelection.get(),
                                                            Direction="하",
                                                            Station= self.TStationSelection.get())

                for TableContent in TimeTableContentLEFT[:-2] :
                    self.TListBoxLEFT.insert(tk.END, f'{TableContent[0]} | {TableContent[1][:-3]}')

                for TableContent in TimeTableContentLEFT[-2:] :
                    Dest = self.CSV.GetTrainDestination(Direction = "상", Station = self.TStationSelection.get(), DayType = self.TDayTypeSelection.get(), TargetTime = TableContent[1])
                    self.TListBoxLEFT.insert(tk.END, f'{TableContent[0]} | {TableContent[1][:-3]} ({Dest} 행)')

                for TableContent in TimeTableContentRIGHT[:-2]:
                    self.TListBoxRIGHT.insert(tk.END, f'{TableContent[0]} | {TableContent[1][:-3]}')
                    
                for TableContent in TimeTableContentRIGHT[-2:]:
                    Dest = self.CSV.GetTrainDestination(Direction = "하", Station = self.TStationSelection.get(), DayType = self.TDayTypeSelection.get(), TargetTime = TableContent[1])
                    self.TListBoxRIGHT.insert(tk.END, f'{TableContent[0]} | {TableContent[1][:-3]} ({Dest} 행)')

                self.TFirstTrainLEFTVar.set(f'{self.TListBoxLEFT.get(0)}')
                self.TLastTrainLEFTVar.set(f'{self.TListBoxLEFT.get(self.TListBoxLEFT.size()-2)}')
                self.TLastTrainLEFTVar2.set(f'{self.TListBoxLEFT.get(self.TListBoxLEFT.size()-1)}')

                self.TFirstTrainRIGHTVar.set(f'{self.TListBoxRIGHT.get(0)}')
                self.TLastTrainRIGHTVar.set(f'{self.TListBoxRIGHT.get(self.TListBoxRIGHT.size()-2)}')
                self.TLastTrainRIGHTVar2.set(f'{self.TListBoxRIGHT.get(self.TListBoxRIGHT.size()-1)}')

                
            def ChangeLine(self):
                if self.CSV.SetLine(self.TLineSelection2.get()) == -1:
                    self.TLineSelection2.set(self.TLineSelection.get())
                    return -1
                self.TLineSelection.set(self.TLineSelection2.get())
                self.StationList = self.CSV.GetStationList()
                self.TStationSelection.set(self.StationList[0])
                self.TComboBox['values'] = self.StationList
                self.TFrame3.config(text=f'{self.StationList[0]} 방면')
                self.TFrame4.config(text=f'{self.StationList[-1]} 방면')
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
                self.StationList = self.CSV.GetStationList()
                self.DayTypeList = self.CSV.GetDayTypeList()
                self.TLineSelection = tk.IntVar(value = TopWinLine)
                self.TLineSelection2 = tk.IntVar(value = TopWinLine)
                self.TDirectionSelection = tk.StringVar(value = "상")
                self.TDayTypeSelection = tk.StringVar(value = TopWinDayType)

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
                            textvariable = self.TLineSelection2, command = self.ChangeLine)

                self.TRadioButtonGroup0 = []
                self.TRadioButtonGroup0.append( tk.Radiobutton(master = self.TFrame1, text = f'{self.StationList[0]} 방면',
                                                   variable = self.TDirectionSelection, value = "상", command = self.UpdateTreeView)
                                                )
                
                self.TRadioButtonGroup0.append( tk.Radiobutton(master = self.TFrame1, text = f'{self.StationList[-1]} 방면',
                                                   variable = self.TDirectionSelection, value = "하", command = self.UpdateTreeView)
                                                )
                
                self.TRadioButtonGroup0[0].pack(side=tk.TOP, anchor="w")
                self.TRadioButtonGroup0[1].pack(side=tk.TOP, anchor="w")
                        

                for DayType in self.DayTypeList:
                    TRadioButton1 = tk.Radiobutton(master = self.TFrame2, text=DayType, variable = self.TDayTypeSelection, value=DayType, command = self.UpdateTreeView)
                    TRadioButton1.pack(side=tk.TOP, anchor="w")

                self.TreeView = ttk.Treeview(master = self)
                self.TreeView['show'] = 'headings'
                

                ScrollX = tk.Scrollbar(master = self, orient = tk.HORIZONTAL)
                ScrollY = tk.Scrollbar(master = self, orient = tk.VERTICAL)

                SizeGrip = ttk.Sizegrip(master = self)
                
                self.TreeView.config(xscrollcommand = ScrollX.set, yscrollcommand = ScrollY.set)
                ScrollX.config(command=self.TreeView.xview)
                ScrollY.config(command=self.TreeView.yview)

                self.TFrame0.pack(fill=tk.BOTH)
                self.TFrame1.pack(fill=tk.BOTH)
                self.TFrame2.pack(fill=tk.BOTH)
                self.TSpinBox.pack(fill=tk.BOTH, padx = 2, pady = 2)
                self.TreeView.grid(row=0, column=1, sticky="nswe")
                ScrollX.grid(row = 1, column = 1, sticky = "ew")
                ScrollY.grid(row = 0, column = 2, sticky = "sn")
                SizeGrip.grid(row=1, column=2, sticky=tk.SE)

            def UpdateTreeView(self):
                self.TreeView.delete(*self.TreeView.get_children()) #Treeview 내용 제거

                if self.TDirectionSelection.get() == "상":
                    self.TreeView['columns'] = ['열차번호'] + self.StationList[::-1]
                else :
                    self.TreeView['columns'] = ['열차번호'] + self.StationList
                
                for col in self.TreeView['columns']:
                    self.TreeView.column(col, anchor=tk.CENTER, width=60, stretch=False) 
                    self.TreeView.heading( col, text=col, anchor=tk.CENTER)

                TrainDict = self.CSV.GetTrainDict(DayType = self.TDayTypeSelection.get(),
                                                  Direction = self.TDirectionSelection.get())


                for key, val in TrainDict.items():
                    newlist = [key]
                    newlist2=[]
                    for el in val: #분까지만 표시
                        if el != None:
                            newlist2.append(el[:-3])
                        else:
                            newlist2.append(None)
                        
                    if self.TDirectionSelection.get() == "상" :
                        newlist.extend(newlist2[::-1])
                    else:
                        newlist.extend(newlist2)
                        
                    self.TreeView.insert(parent='', index='end', iid=key, values=newlist)


            def ChangeLine(self):
                if self.CSV.SetLine(self.TLineSelection2.get()) == -1:
                    self.TLineSelection2.set(self.TLineSelection.get())
                    return -1
                self.TLineSelection.set(self.TLineSelection2.get())
                self.StationList = self.CSV.GetStationList()
                self.TRadioButtonGroup0[0].config(text = f'{self.StationList[0]} 방면')
                self.TRadioButtonGroup0[1].config(text = f'{self.StationList[-1]} 방면')                    
                self.UpdateTreeView()


                
#a = TimeTableWindow(master = tk.Tk(), Line = 2, Station="대실", DayType ="평일")
#a.mainloop()
