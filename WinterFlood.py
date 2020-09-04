# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 15:54:30 2020

@author: natha
"""
#Import Libaries
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class Processor():
    
    def __init__(self, RawData):
        self.RawData = RawData
        
        self.VWAP, self.Quantities = self.CreateDataFrames()
        self.CalculateVWAP()
                
        # Save stocks 
        self.SaveStockVWAP1()
        self.SaveStockTypeVWAP1()
        self.SaveStockVWAP2()
        self.SaveStockTypeVWAP2()


    def CreateDataFrames(self):
        #Extract all unique stocknames and trade types
        StockNames = RawData["epic"].unique()
        TTNames = RawData["trade type"].unique()

        #append overall to trade types in order to hold overall stats for each stock
        TTNames = np.append(TTNames, 'Overall')
        
        #Create Dataframe to hold VWAP and set values to 0 
        VWAP = pd.DataFrame(columns=StockNames, index=TTNames)
        
        for col in VWAP.columns:
            VWAP[col].values[:] = 0
            
        #Copy VWAP table to hold quantities
        Quantities = VWAP.copy() 
        
        return VWAP, Quantities

    def CalculateVWAP(self):
        #For each trade 
        for i in range(self.RawData.shape[0]):
            Row = self.RawData.loc[i,['epic', 'trade type', 'quantity', 'price']] #store relevent data regarding current trade
            
            self.VWAP.loc[Row[1], Row[0]] += (Row[2] * Row[3]) #add price x quantity to appropriet VWAP location for stock/trade type
            self.Quantities.loc[Row[1], Row[0]] += Row[2] #add quantity to quantity table
            
            self.VWAP.loc['Overall', Row[0]] += (Row[2] * Row[3]) #Repeat above for stock overall 
            self.Quantities.loc['Overall', Row[0]] += Row[2]
        
        #loop through VWAP table dividing by 
        for col in self.VWAP.columns:
            for index in self.VWAP.index:
                if (not(self.VWAP.loc[index,col] == 0)):
                    self.VWAP.loc[index,col] /= self.Quantities.loc[index,col]

    def PrintVWAP(self): #printVWAP, used for debugging
        print(self.VWAP)



    def SaveStockVWAP1(self):       #Save just overall stock VWAP in style of input data
        EpicNames = RawData["epic"].unique()  #get stock short and long names as well as VWAP overall data
        StockNames = RawData["isin"].unique()
        StockVWAP = self.VWAP.iloc[self.VWAP.shape[0]-1,:] 
        
        
        Dict= {'epic':EpicNames, 'isin':StockNames, 'tradetype':'All', 'vwap': StockVWAP} #set up dictionary with heading titles and data
        df = pd.DataFrame(data=Dict) #define dataframe
        df.to_csv('D:/Work/WinterFlood/StockOnlyVWAP.csv', index = False)   #save to csv
        
        
        
        
    def SaveStockTypeVWAP1(self):       #Save individual trade type VWAP data in input style
        EpicNames = RawData["epic"].unique()   #get stock short and long names as well as VWAP overall data and trade types
        StockNames = RawData["isin"].unique()     
        TTNames = RawData["trade type"].unique()
        StockVWAP = self.VWAP.iloc[:self.VWAP.shape[0]-1,:]
        
        
        EpicCol = []  #create empty lists to hold each column in final datafile
        StockCol = []
        TTCol = []
        VWAPCol = []
        
                
        for col in range(self.VWAP.shape[1]):
            for tt in range(self.VWAP.shape[0]-1): #for each cell of VWAP Table
                EpicCol.append(EpicNames[col])  #append data to relevent lists
                StockCol.append(StockNames[col])
                TTCol.append(TTNames[tt])     
                VWAPCol.append(StockVWAP.iloc[col,tt])
        
        
        
        
        Dict = {'epic':EpicCol, 'isin':StockCol, 'tradetype':TTCol, 'vwap':VWAPCol} #construct dictionary from lists
        df = pd.DataFrame(data=Dict)#define dataframe from dictionary
        df.to_csv('D:/Work/WinterFlood/StockTypeVWAP.csv', index = False) #save to csv




    def SaveStockVWAP2(self): #Save in VWAP table style 
        StockVWAP = self.VWAP.iloc[self.VWAP.shape[0]-1,:]#get Vwop stats of just overall
        StockVWAP.to_csv('D:/Work/WinterFlood/StockOnlyVWAP2.csv')#save to csv

    def SaveStockTypeVWAP2(self):#Save in VWAP table style 
        StockVWAP = self.VWAP.iloc[:self.VWAP.shape[0]-1,:]     #get all vwop stats except overall 
        StockVWAP.T.to_csv('D:/Work/WinterFlood/StockTypeVWAP2.csv')        #save to csv











#define interface class
class UserInterface(Tk): #inherits from Tk which is the main window class
    def __init__(self, VWAP): #requires VWAP table
        super(UserInterface, self).__init__()
        self.VWAP = VWAP  #Save VWAP table
        
        self.title('WinterFlood Project') #set title and window minimum size
        self.minsize(400,550)
        
        self.CreateStockList() #Create UI elements
        self.CreateTradeList()
        self.CreatePlotButton()              
        self.CreateCanvas()
        
        
        self.ButtonPlot() #execute initial plotting of default stock/tradetype choices
        
        #add label to explain application functionality
        self.Explain = Label(self, text ="Press plot to see a VWOP graph of your selected epic and trade types. The red line indicates the overall VWOP of that epic", wraplength = 150)
        self.Explain.grid(column = 1, row = 0, sticky = S)#add to layout
        
        
    def CreateStockList(self): 
        StockFrame = Frame(self)  #create frame to hold stocklist
        StockFrame.grid(column = 1, row = 0, sticky = W, padx = 10, pady = 10) #add to layout
        
        StockLabel = Label(StockFrame, text = 'Please Select an Epic:') #add label to frame 
        StockLabel.pack() #pack to frame

        self.StockList = Listbox(StockFrame, exportselection=0) #create listbox in frame
        for col in self.VWAP.columns: #populate listbox with stock names
            self.StockList.insert(END, col)
   
        self.StockList.pack() #pack to frame
        self.StockList.selection_set(0) #set default selection to first element


    def CreateTradeList(self):
        TradeFrame = Frame(self) #create frame to hold tradelist
        TradeFrame.grid(column = 1, row = 0, sticky = E, padx = 10, pady = 10)   #add to layout
        
        TradeLabel = Label(TradeFrame, text = 'Please Select Trade Types:') #create label in frame 
        TradeLabel.pack()# pack to frame

        self.TradeList = Listbox(TradeFrame, selectmode = MULTIPLE, exportselection=0) #create listbox wich allows multiple selections in frame
        for index in self.VWAP.index:
            if not(index =='Overall'):
                self.TradeList.insert(END, index) #populate with all trade types except overall
                
        self.TradeList.pack()#pack to frame
        self.TradeList.selection_set(0, last = self.VWAP.index.shape[0]) #select all elements by default 
        
    def CreateCanvas(self): #create canvas with embedded matplotlib figure
        
        self.Fig = Figure() #create matplotlib figure
        self.PlottingCanvas = FigureCanvasTkAgg(self.Fig, self) #create canvas with figure embedded
        self.PlottingCanvas.get_tk_widget().grid(column = 1, row = 2, padx = 10, pady = 10)        #add to grid layout
        self.ToPlot = self.Fig.add_subplot(111) #create subplot to plot into
        
        PlotFrame = Frame(self)  #create frame for navigation toolbar
        PlotFrame.grid(column = 1, row = 3)#place toolbar frame on grid
        toolbar = NavigationToolbar2Tk(self.PlottingCanvas, PlotFrame) #create toolbar on canvas
        toolbar.update() 
        
        
    def UpdateCanvas(self, Stock, TradeTypes):   #function to update plot, requires list of trade types and a selected stop
        Values = [] #create lists to hold values to plot
        UsedTrades = []
        for col in TradeTypes: #for each trade type
            Value = self.VWAP.loc[col,Stock] #get VWAP value
            if not(Value == 0): #if trades of this type exist for this stock
                Values.append(Value)     #append VWAP and trade type value and label list to be plotted 
                UsedTrades.append(col)   
        
        
        Overall = self.VWAP.loc['Overall',Stock] #get overall VWAP value for selected stock
        Values -= Overall    #center values around the overall value
        
        
        self.ToPlot.cla() #clear plto
        self.ToPlot.barh(UsedTrades, Values,left = Overall)     #plot horizontal bar chart centered on overall value
        self.ToPlot.grid(which = 'major')#add major gridlines
        self.ToPlot.axvline(Overall, color = 'red') # add red line at overall value
        
        self.ToPlot.set_title(Stock + ' VWAP of Selected Trade Types') #add title and axis labels
        self.ToPlot.set_ylabel('Trade Types')
        self.ToPlot.set_xlabel('VWAP')
            
        self.PlottingCanvas.draw()  #re-draw canvas
        
        
    def CreatePlotButton(self): 
        self.PlotButton = ttk.Button(self, text = 'Plot', command = self.ButtonPlot) #create button that calls ButtonPlot
        self.PlotButton.grid(column = 1, row = 1) #add to grid layout


    def ButtonPlot(self):   #function which exectutes when plot button is pressed
        StockID = self.StockList.curselection() #get selections for both list boxes as indexes
        TradeIDs = self.TradeList.curselection()
        
        
        SelectedStock = self.VWAP.columns[StockID]  #get stock name
        TradeTypes = []
        for Index in TradeIDs:    #for each trade ID, get trade name
            TradeTypes.append(self.VWAP.index[Index])
        
        self.UpdateCanvas(SelectedStock, TradeTypes) #update graph with selected values 





#Read in Raw Data
RawData = pd.read_csv("D:/Work/WinterFlood/market_trades.csv")
Pr = Processor(RawData) #create instance of processor
Window = UserInterface(Pr.VWAP)#create instance of the interface
Window.mainloop()






