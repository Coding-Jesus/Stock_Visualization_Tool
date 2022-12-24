from operator import index
from tracemalloc import start
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import yfinance as yf
import datetime as dt
from mplfinance.original_flavor import candlestick_ohlc
from pandas_datareader import data as pdr

yf.pdr_override() # Activate yahoo finance workaround

smasUsed=[20] # Choose smas

stock=input("Enter a ticker symbol: ") #Asks for a stock ticker

start=str(input("Enter Start Date: ")) #Sets start point of dataframe

end = str(input("Enter End Date: ")) #Sets end point of datatframe

while stock != "quit": #Runs this loop until user enters 'quit' (can do many stocks in a row)

    prices=pdr.get_data_yahoo(stock,start,end) #Fetches stock price data, saves as dataframe

    fig,ax1 = plt.subplots() #Create Plots
    #Calculate moving averages
    for x in smasUsed: #This for loop calculates the SMAs for the stated periods and appends to dataframe
        sma=x
        prices['SMA_'+str(sma)] =prices.iloc[:,4].rolling(window=sma).mean() #Calculates sma and creates col

    #Calculate Bollinger Bnads 
    BBperiod=20 #Choose moving avg
    stdev=2
    prices['SMA'+str(BBperiod)]=prices.iloc[:,4].rolling(window=sma).mean() #Calculates sma and creates col
    prices['STDEV']=prices.iloc[:,4].rolling(window=BBperiod).std() #Calculatesstandard deviation and creates col
    prices['LowerBand']=prices['SMA'+str(BBperiod)]-(stdev*prices['STDEV']) #Calculates lower bollinger band
    prices['UpperBand']=prices['SMA'+str(BBperiod)]+(stdev*prices['STDEV']) #Calculates upper band
    prices["Date"]=mdates.date2num(prices.index) #Creates a date column stored in number format (for OHCL bars)


    #Calculate 10.4.4 stochastic
    Period=10 #Choose stoch period
    K=4
    D=4
    prices["RolHigh"] = prices["High"].rolling(window=Period).max() #Finds high of period
    prices["RolLow"] = prices["Low"].rolling(window=Period).min() #Finds low of period
    prices["stok"] = ((prices["Adj Close"]-prices["RolLow"]/prices["RolHigh"]-prices["RolLow"]))*100 #Finds 10.1 stoch
    prices["K"] = prices["stok"].rolling(window=K).mean() #Finds 10.4 stoch
    prices["D"] = prices["K"].rolling(window=D).mean() #Finds 10.4 stoch
    prices["GD"]=prices["High"] #Create GD column to store green dots
    ohlc = [] #Create OHLC arry which will store price data for the candlestick chart

    #Delete extra dates
    prices=prices.iloc[max(smasUsed):]

    greenDotDate=[] #Stores dates of green dots
    greenDot=[] #Stores Values of Green Dots
    lastK=0 #Will store Yesterday's fast stoch
    lastD=0 #Will store yesterday's slow stoch
    lastLow=0 # Will store yesterdays lower 
    lastClose=0 #Will stores yesterdays close
    lastLowBB=0 # Will store yesterdays lower band

    #Go through price history to create candlesticks and GD+Blue dots
    for i in prices.index:
        #Append OHLC prices to make the candle stick
        append_me = prices["Date"][i], prices["Open"][i], prices["High"][i],prices["Low"][i], prices["Adj Close"][i], prices["Volume"][i]
        ohlc.append(append_me)

        #Check for Green Dot
        if prices["K"][i]>prices['D'][i] and lastK<lastD and lastK <60:

            #plt.Circle((prices["Date"][i].prices["High"][i]),1)
            #plt.bar(prices["Date"][i],1,1.1bottom=prices["High"][i]*1.01,color='g')
            plt.plot(prices["Date"][i],prices["High"][i]+1, marker="D", ms=4, ls="", color='g') #Plot green dot

            greenDot.append(i) #Store green dot date
            greenDot.append(prices["High"][i]) #Store green dot value

        #Check for Lower Bollinger Band Bounce
        if ((lastLow<lastLowBB) or (prices['Low'][i]<prices['LowerBand'][i])) and (prices['Adj Close'][i]>lastClose and prices['Adj Close'][i]>prices['LowerBand'][i]) and lastK <60:
            plt.plot(prices["Date"][i], prices["Low"][i]-1, marker="D", ms=4, ls="", color='r') #Plot blue dot

        #Store Values
        lastK=prices['K'][i]
        lastD=prices['D'][i]
        lastLow=prices['Low'][i]
        lastClose=prices['Adj Close'][i]
        lastLowBB=prices['LowerBand'][i]


    #Plot moving averages and BBands
    for x in smasUsed: #This for loop calculates the EMAs for the stated periods and appends to dataframe
        sma=x
        prices['SMA_'+str(sma)].plot(label='close')
    prices['UpperBand'].plot(label='close', color='lightgray')
    prices['LowerBand'].plot(label='close', color='lightgray')

    #Plot candlesticks
    candlestick_ohlc(ax1, ohlc, width=.5, colorup='g', colordown='r', alpha=0.75)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) #Change x axis back to datestamps
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(8)) #Add more x axis labels
    plt.tick_params(axis='x', rotation=45) #Rotate dates for readability

    #Pivot Points
    pivots=[] #Stores pivot Values
    dates=[] # Stores Dates corresponding tot those pivot values
    counter=0 #will keep track of whether a certain value is a pivot
    lastPivot=0 #Will store the last Pivot value

    Range=[0, 0, 0, 0, 0,0, 0, 0, 0, 0]
    dateRange=[0, 0, 0, 0, 0,0, 0, 0, 0, 0]
    for i in prices.index: #Iterates through the price history
        currentMax=max(Range, default=0) #Determines the maximum value of the 10 item array, identifying a potnetial pivot point
        value=round(prices["High"][i],2) #Receives next high value from the dataframe 

        Range=Range[1:9] #Cuts Range array to only the most recent 9 values
        Range.append(value) #Adds newest high value to the array
        dateRange=dateRange[1:9] #Cuts Date array to only the most recent 9 values
        dateRange.append(i) #Adds newest date to the array 

        if currentMax == max(Range, default=0): #If statement that check is the max stays the same
            counter+=1 #If yes add 1 to counter
        else:
            counter=0 #Otherwise new potential pivot so reset the counter
        if counter==5: #Checks if we have identified a pivot
            lastPivot=currentMax #Assigns last pivot to the current max value
            dateloc=Range.index(lastPivot) #Finds index of the range array that is the pivot value
            lastDate=dateRange[dateloc] #Gets date corresponding to that index
            pivots.append(currentMax) #Adds pivot to pivot array
            dates.append(lastDate) #Adds pivot date to date array
    print()

    timeD=dt.timedelta(days=30) #Sets length of dotted line on chart

    for index in range(len(pivots)) : #Iterates through pivot array

        #print(str(pivots[index])+": "+str(dates[index])) #Prints pivot, Date couple
        plt.plot_date([dates[index]-(timeD*.075), dates[index]+timeD], #Plots horizontal line at pivot value
                    [pivots[index], pivots[index]], linestyle="--", linewidth=1, marker=",")
        plt.annotate(str(pivots[index]), (mdates.date2num(dates[index]), pivots[index]), xytext=(-10, 7),
                textcoords='offset points',fontsize=7, arrowprops=dict(arrowstyle='-|>'))

    plt.xlabel('Date') #Set x axis label
    plt.ylabel('Price') #Set y axis label
    plt.title(stock+" - Daily") #Set title
    plt.ylim(prices["Low"].min(), prices["High"].max()*1.05) #Add margins
    #plt.yscale("log")

    plt.show()
    #print()
    stock = input("Enter the ticker Symbol : ") # Asks for new stock
