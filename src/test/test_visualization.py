import pandas as pd
import matplotlib.pyplot as plt

from src.main.stock_market.strategy.strategy_name.StrategyBigSmall_1 import StrategyBigSmall_1


class TestTickVisualization:
	def __init__(self):
		self.strategyBigSmall = StrategyBigSmall_1()

	def demo0(self):
		lTimehms = 224806
		df = pd.read_csv('cache/ticks_2_0.csv')
		print('---big {}---'.format(lTimehms))
		qv.strategyBigSmall.parse_qty(df, lTimehms, 'big')
		print('---small {}---'.format(lTimehms))
		qv.strategyBigSmall.parse_qty(df, lTimehms, 'small')

		# df['addSubNQty'].plot()
		# plt.show()
		self.plot_show(
			qv.strategyBigSmall.filter_qty(df, lTimehms, 21, 'big')
		)

		df = pd.read_csv('cache/ticks_2_7.csv')
		print('---big {}---'.format(lTimehms))
		qv.strategyBigSmall.parse_qty(df, lTimehms, 'big')
		print('---small {}---'.format(lTimehms))
		qv.strategyBigSmall.parse_qty(df, lTimehms, 'small')
		pass

	def plot_show(self, df):
		ary1 = []
		ary2 = []
		for index, row in df.iterrows():
			ary1.append(row['lTimehms'])
			ary2.append(row['addSubNQty'])
		plt.plot(ary1, ary2)
		plt.ylabel('quote')
		plt.xlabel('time')
		plt.show()
		pass


if __name__ == '__main__':
	# My Data Structure
	qv = TestTickVisualization()
	qv.demo0()
	# qv.demo1()

	exit()
