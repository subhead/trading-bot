from poloniex import poloniex
import urllib, json

class BotChart(object):
	def __init__(self, exchange, pair, period):
		self.pair = pair
		self.period = period

		self.startTime = 1491048000
		self.endTime = 1491591200
		
		if (exchange == "poloniex"):
			self.conn = poloniex('key goes here','Secret goes here')

			self.data = self.conn.api_query("returnChartData",{"currencyPair":self.pair,"start":self.startTime,"end":self.endTime,"period":self.period})

		if (exchange == "bittrex"):
			url = "https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName="+self.pair+"&tickInterval="+self.period+"&_="+str(self.startTime)
			response = urllib.urlopen(url)
			rawdata = json.loads(response.read())

			self.data = rawdata["result"]


	def getPoints(self):
		return self.data
