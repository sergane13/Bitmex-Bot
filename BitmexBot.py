import bitmex
import pandas as pd
import numpy as np
import csv

from keys_testnet import public as test_PK
from keys_testnet import secret as test_SK
from keys import public_key as PK
from keys import secret_key as SK


class BitmexBot:

    # constructor
    def __init__(self, symbol):
        testOrReal = input("Do you connect to real Bitmex or testnet('r' or 't'): ")
        if testOrReal == 'r':
            self.client = bitmex.bitmex(test=False, api_key=PK, api_secret=SK)
            self.symbol = symbol
            print("CONNECTED")
        elif testOrReal == 't':
            self.client = bitmex.bitmex(test=True, api_key=test_PK, api_secret=test_SK)
            self.symbol = symbol
            print("CONNECTED")

    # set close price and get the last 900 candles in an array
    def getClosePrices(self, bin_size):
        raw_candles = self.client.Trade.Trade_getBucketed(binSize=bin_size, symbol=self.symbol, count=900, reverse=True).result()
        self.lastClose = raw_candles[0][0]['close']
        self.candles = []

        for i in range(0, 900):
            self.candles.append(raw_candles[0][900 - 1 - i]['close'])

    # set WMA (Weighted Moving Average)
    def WMA(self, series=None, period=1):
        if series is None:
            gauss_sum = period*(period+1)
            gauss_sum /= 2
            WMA_vals = []
            aux = 0

            for i in range(0, period - 2):
                WMA_vals.append(0)

            for i in range(period - 1, len(self.candles)):
                n = period
                sum = 0

                while n >= 1:
                    sum += self.candles[aux + n-1] * n
                    n -= 1

                sum /= gauss_sum
                WMA_vals.append(sum)
                aux += 1

            WMA = pd.Series(WMA_vals)

            for i in range(0, period - 2):
                WMA[i] = np.nan

            return WMA
        else:
            gauss_sum = period*(period+1)
            gauss_sum /= 2
            WMA_vals = []
            aux = 0

            for i in range(0, period - 2):
                WMA_vals.append(0)

            for i in range(period - 1, len(series)):
                n = period
                sum = 0

                while n >= 1:
                    sum += series[aux + n-1] * n
                    n -= 1

                sum /= gauss_sum
                WMA_vals.append(sum)
                aux += 1

            WMA = pd.Series(WMA_vals)

            for i in range(0, period - 2):
                WMA[i] = np.nan

            return WMA

    # Set HMA (Hull Moving Average)
    def HMA(self, period):
        first_wma = 2 * self.WMA(period=int(period / 2))
        second_wma = self.WMA(period=period)
        result_wma = first_wma - second_wma

        hma = self.WMA(series=result_wma, period=int(np.sqrt(period)))
        return hma[len(hma) - 1]

    """
    ##################---Order functions---##################
    """
    def buy(self, qty):
        # buy crypto token/coin
        order = self.client.Order.Order_new(symbol=self.symbol, orderQty=qty, ordType="Market").result()
        self.registerOrder(order[0])

    def sell(self, qty):
        # sell crypto token/coin
        order = self.client.Order.Order_new(symbol=self.symbol, orderQty=-1*qty, ordType="Market").result()
        self.registerOrder(order[0])

    def buy_stop(self, qty):
        # Stop Market Order
        last_buy = self.client.OrderBook.OrderBook_getL2(symbol=self.symbol, depth=1).result()[0][1]['price']
        stop_price = np.floor(last_buy*0.995)
        self.client.Order.Order_new(symbol=self.symbol, orderQty=qty, ordType="Market").result()
        self.client.Order.Order_new(symbol=self.symbol, orderQty=-1*qty, stopPx=stop_price).result()

    def sell_stopself(self, qty):
        # Stop Market Order
        last_sell = self.client.OrderBook.OrderBook_getL2(symbol=self.symbol, depth=1).result()[0][0]['price']
        stop_price = np.floor(last_sell*1.005)
        self.client.Order.Order_new(symbol=self.symbol, orderQty=-1*qty, ordType="Market").result()
        self.client.Order.Order_new(symbol=self.symbol, orderQty=qty, stopPx=stop_price).result()

    # Contracts available to use
    def get_available_contracts(self):
        last_buy = self.client.OrderBook.OrderBook_getL2(symbol="XBT", depth=1).result()[0][1]['price']
        account = self.client.User.User_getWallet().result()[0]['amount']/10000
        return np.floor(account * last_buy * 0.97)

    # Write orders in file
    @staticmethod
    def register_order(self, order):
        with open('orders.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([order['transactTime'], order['price'], order['side']])

    # Write recent trades in file
    @staticmethod
    def register_trade(self, trade):
        with open('recentTrades.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([trade['symbol'],trade['timestamp'], trade['side'], trade['size'], trade['price']])

    # Write a row to a file
    @staticmethod
    def write_to_file(self, file_name, row):
        with open(file_name, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    # Last buy price
    def last_buy(self):
        last_buy = self.client.OrderBook.OrderBook_getL2(symbol=self.symbol, depth=1).result()[0][1]['price']
        return last_buy

    # Last sell price
    def last_sell(self):
        last_buy = self.client.OrderBook.OrderBook_getL2(symbol=self.symbol, depth=1).result()[0][0]['price']
        return last_buy

    # Order book history
    def recent_trades(self, start_time, end_time):
        return self.client.Trade.Trade_get(symbol="XBT", reverse=True, startTime=start_time, endTime=end_time).result()[0]
