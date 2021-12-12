import sys 
from liveplot import LivePlot
from DataProcesser import DataProcesser
from BitmexBot import BitmexBot

myPlot = LivePlot()
myDP = DataProcesser()
myOrder = BitmexBot("XBT")

myDP.start()
myPlot.plot()
sys.exit()
