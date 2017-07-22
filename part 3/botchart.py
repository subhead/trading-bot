from poloniex import poloniex

class BotChart(object):
	def __init__(self, exchange, pair, period):
		self.conn = poloniex('key goes here','Secret goes here')

		self.pair = pair
		self.period = period

		self.startTime = 1491048000
		self.endTime = 1491591200

		self.data = self.conn.api_query("returnChartData",{"currencyPair":self.pair,"start":self.startTime,"end":self.endTime,"period":self.period})

	def getPoints(self):
		return self.data
