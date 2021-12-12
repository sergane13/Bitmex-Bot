import matplotlib 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime
import sys
from time import sleep
from matplotlib import style


class LivePlot:

    # Display OBV values from the last 900 candles
    def animate(self, i):
        graph_data = open('OBV_vals.csv', 'r').read()
        lines = graph_data.split('\n')
        xs = []
        ys = []

        for line in lines:
            if len(line) > 1:
                x, y = line.split(',')
                date_time_str = x
                date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
                xs.append(date_time_obj)
                ys.append(float(y))

        plt.cla()
        plt.plot(xs, ys)

    def plot(self):

        sleep(7)
        style.use('fivethirtyeight')

        ani = animation.FuncAnimation(plt.gcf(), self.animate, interval=1000)
        matplotlib.rc('lines', linewidth=1, linestyle='-.')
        plt.tight_layout() 
        plt.show()
        sys.exit()
