from BitmexBot import BitmexBot
from datetime import datetime as dt
from time import sleep
from threading import *
import sys


class DataProcesser(Thread):

	# OBV indicator(On-Balance Volume Indicator)
	def OBV(self, trades):

		result = 0

		for trade in trades:

			if trade['side'] == 'Sell':
				result -= trade['size']
			else:
				result += trade['size']

		return result

	# Feedback from command line
	def run(self):
		sleep_time = 0

		if len(sys.argv) == 2:

			sleep_time = int(sys.argv[1])
			print("Creating new OBV_vals.csv file...")
			open('OBV_vals.csv', 'w').close()
			sleep(1)
			print("New file created")

		else:
			print("Invalid amount of arguments.")
			print("Syntax: python3 bot.py <sleep time(in seconds)> ")
			sys.exit()

		# Init
		client = BitmexBot("XBT")
		start_time = dt.utcnow()
		end_time = dt.utcnow()
		my_obv = 0

		# Infinite bubble where you see OBV values
		while True:

			sleep(sleep_time)

			end_time = dt.utcnow()
			recent_trades = client.RecentTrades(startTime=start_time, endTime=end_time)
			start_time = end_time
			my_obv += self.OBV(recent_trades)

			client.writeToFile(fileName='OBV_vals.csv', row=[end_time, my_obv])
