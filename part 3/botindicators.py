import numpy as np

class BotIndicators(object):
	def __init__(self):
		 pass

	def movingAverage(self, dataPoints, period):
		if (len(dataPoints) > 1):
			return sum(dataPoints[-period:]) / float(len(dataPoints[-period:]))
		
	def momentum (self, dataPoints, period=14):
		if (len(dataPoints) > period -1):
			return dataPoints[-1] * 100 / dataPoints[-period]
		
	def RSI (self, prices, period=14):
		deltas = np.diff(prices)
		seed = deltas[:period+1]
		up = seed[seed >= 0].sum()/period
		down = -seed[seed < 0].sum()/period
		rs = up/down
		rsi = np.zeros_like(prices)
		rsi[:period] = 100. - 100./(1. + rs)

		for i in range(period, len(prices)):
			delta = deltas[i - 1]  # cause the diff is 1 shorter

			if delta > 0:
				upval = delta
				downval = 0.
			else:
				upval = 0.
				downval = -delta

			up = (up*(period - 1) + upval)/period
			down = (down*(period - 1) + downval)/period

			rs = up/down
			rsi[i] = 100. - 100./(1. + rs)

		if len(prices) > period:
			return rsi[-1]
		else:
			return 50 # output a neutral amount until enough prices in list

