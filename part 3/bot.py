import time
import sys, getopt
import datetime
from poloniex import poloniex
from Tkinter import *
import Tkinter as tk

class TradingStrategy():
	def __init__(self):
		self.values = []
		self.pair = "BTC_XMR"
		self.conn = poloniex('79GA9FNK-4UQ9665O-LQQJ2CT4-57Y378P5','c6c34ee11cd0cb65b0fb1930974f6bbb1adde2052c2e9cd225de7f4408f9d228e4a2ad9c057601e6626eb83576c6b08fa43c9e034d9b72ca037dd74a1801bb16')
		self.period = 1800
		self.inTrade = False

	def updateValue(self):
		currentValues = self.conn.api_query("returnTicker")
		currentPairPrice = currentValues[self.pair]["last"]

		self.values.append(currentPairPrice)

	def getValues(self):
		return self.values

	def getTradeEntries(self):
		self.tradeEntries = []
		for index,val in enumerate(self.values):
			
			if (len(self.values) > 1):
				if (self.values[index] > self.resistanceTrendLines[index]):
					self.tradeEntries.append(self.values[index])
				else:
					self.tradeEntries.append(0)

		return self.tradeEntries

	def getTradeExits(self):
		self.tradeEntries = []
		for index,val in enumerate(self.values):
			
			if (len(self.movingAverageValues) > 3):
				if ( (len(self.values) > index) and (len(self.movingAverageValues) > index) and (self.values[index] < self.movingAverageValues[index])):
					self.tradeEntries.append(self.values[index])
				else:
					self.tradeEntries.append(0)

		return self.tradeEntries

	def getMovingAverage(self,period):
		self.movingAverageValues = []
		for index,val in enumerate(self.values):
			sublist = self.values[0:index]
			
			if (len(sublist) > 1):
				self.movingAverageValues.append(sum(sublist[-period:]) / float(len(sublist[-period:])))

		return self.movingAverageValues

	def getResistanceTrendLines(self):
		self.resistanceTrendLines = []
		localMaxes = []
		currentResistance = 0
		
		for index,val in enumerate(self.values):
			if (index > 2):

				if ( (float(self.values[index-2]) > float(self.values[index-1])) and (float(self.values[index-2] > float(self.values[index-3]))) ):
					numberOfSimilarLocalMaxes = 0

					for oldMax in localMaxes:
						if ( (float(oldMax) > (float(self.values[index-2]) - .0001) ) and (float(oldMax) < (float(self.values[index-2]) + .0001) ) ):
							numberOfSimilarLocalMaxes = numberOfSimilarLocalMaxes + 1

					if (numberOfSimilarLocalMaxes > 2):
						currentResistance = self.values[index-2]

					localMaxes.append(self.values[index-2])
			
				self.resistanceTrendLines[-2] =currentResistance
			
			self.resistanceTrendLines.append(0)

		return self.resistanceTrendLines

	def getBacktestValues(self,startDate,endDate):
		self.values = []
		historicalData = self.conn.api_query("returnChartData",{"currencyPair":self.pair,"start":startDate,"end":endDate,"period":self.period})
		while historicalData:
			nextDataPoint = historicalData.pop(0)
			pairPrice = nextDataPoint['weightedAverage']
			self.values.append(pairPrice)


class Chart(tk.Frame):
	def __init__(self, parent, title, strategy):
		self.Line1 = [0, 100, 10, 0, 50, 200]
		self.tempNumber = 0
		self.backtesting = False
		self.strategy = strategy
		self.parent = parent

		parent.wm_geometry("1200x600")
		Frame.__init__(self, parent)
		self.grid()
		parent.title(title)
		parent.wm_geometry("1200x600")

		for r in range(7):
			parent.rowconfigure(r, weight=1)    
		for c in range(1):
			parent.columnconfigure(c, weight=1)

		self.canvas = tk.Canvas(self, background="black", width="1200", height="400")
		self.canvas.create_line(self.Line1, tag='X', fill='white', width=1)
		self.canvas.grid(row=0,column=0, sticky=W+E+N+S)

		self.startDate = Text(parent, height=2, width=30, state=NORMAL)
		self.startDate.insert(END, "1491048000")
		self.startDate.grid(row=5,column=0, sticky=W+E+N+S)

		self.endDate = Text(parent, height=2, width=30, state=NORMAL)
		self.endDate.insert(END, "1491591200")
		self.endDate.grid(row=6,column=0, sticky=W+E+N+S)

		self.backtestBtn = tk.Button(parent, text="Backtest", command=self.drawBacktest)
		self.backtestBtn.grid(row=7,column=0, sticky=W+E+N+S)

	def drawBacktest(self):
		self.backtesting = True
		self.strategy.getBacktestValues(self.startDate.get("1.0",END).rstrip(),self.endDate.get("1.0",END).rstrip())
		self.update_text(self.parent,self.strategy)
		

	def on_resize(self, event):
		self.replot()

	def append_values(self, x, y):
		self.Line1.append(float(x))
		self.Line1.append(float(y))
		self.canvas.create_line(self.Line1, tag='X', fill='darkblue', width=1)
		self.canvas.grid(row=0,column=0, sticky=W+E+N+S)
		return

	def update_text(self,parent,strategy):
		if not self.backtesting:
			strategy.updateValue()

		self.Line1 = self.getCoordsFromValues(strategy.getValues(),strategy.getValues())
		self.Line2 = self.getCoordsFromValues(strategy.getMovingAverage(15),strategy.getValues())
		self.Line3 = self.getCoordsFromValues(strategy.getResistanceTrendLines(),strategy.getValues())
		self.Line4 = self.getCoordsFromValues(strategy.getTradeEntries(),strategy.getValues())
		self.Line5 = self.getCoordsFromValues(strategy.getTradeExits(),strategy.getValues())

		if (len(self.Line1) > 2):
			self.canvas = tk.Canvas(self, background="black" )
			self.canvas.create_line(self.Line1, tag='X', fill='white', width=1)
			self.canvas.create_line(self.Line2, tag='M', fill='blue', width=1)
			self.canvas.create_line(self.Line3, tag='R', fill='orange', width=1)
			self.canvas.create_line(self.Line4, tag='B', fill='green', width=1)
			self.canvas.create_line(self.Line5, tag='E', fill='red', width=1)
			self.canvas.pack(fill=BOTH,expand=YES)
			self.canvas.grid(row=0,column=0,sticky=W+E+N+S)
		
		if not self.backtesting:
			parent.after(20000,self.update_text,parent,strategy)


	def getCoordsFromValues(self,values,bounds):
		coords = []
		xAxis = 400/ len(bounds)
		maxValue = max(bounds)
		minValue = min(bounds)
		print maxValue
		print minValue
		for value in values:
			if (value > minValue):
				coordValue = float(400) - (((float(value) - float(minValue)) / (float(maxValue)-float(minValue))) * float(400))
			else:
				coordValue = float(400)
			coords.append(float(xAxis))
			coords.append(coordValue)

			xAxis = xAxis + (float(1200) / float(len(values)))

		return coords

	def replot(self):
		w = self.winfo_width()
		h = self.winfo_height()
		max_X = max(self.Line1) + 1e-5
		max_all = 200.0
		coordsX, coordsY, coordsZ = [], [], []
		for n in range(0, self.npoints):
			x = (w * n) / self.npoints
			coordsX.append(x)
 			coordsX.append(h - ((h * (self.Line1[n]+100)) / max_all))
			self.canvas.coords(*coordsX)

def main(argv):
	root = tk.Tk()
	
	strategy = TradingStrategy()

	app = Chart(root, "Trading Bot",strategy)

	root.after(20000,app.update_text(root,strategy))
	app.mainloop()

	return 0

if __name__ == "__main__":
	main(sys.argv[1:])