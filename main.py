from __future__ import (absolute_import, division, print_function, unicode_literals)

import os.path
import sys
import backtrader as bt

from strategies.my_strategy import MyStrategy

def main():
  cerebro = bt.Cerebro()

  modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
  # datapath = os.path.join(modpath, 'data/amzn-2020.csv')
  # datapath = os.path.join(modpath, 'data/nflx-2020.csv')
  # datapath = os.path.join(modpath, 'data/uber-2020.csv')
  datapath = os.path.join(modpath, 'data/tsla-2020.csv')

  data = bt.feeds.GenericCSVData(
    dataname=datapath,
    dtformat='%m/%d/%Y',
    datetime=0,
    close=1,
    open=2,
    high=3,
    low=4,
    volume=5,
    openinterest=-1,
  )

  cerebro.adddata(data)

  cerebro.broker.setcash(100000.0)
  cerebro.addstrategy(MyStrategy)

  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.run()

  print('\n\nFinal Portfolio Value: %.2f' % cerebro.broker.getvalue())
  
  cerebro.plot()

if __name__ == '__main__':
  main()
