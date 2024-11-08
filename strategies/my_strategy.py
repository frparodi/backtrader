import backtrader as bt

class MyStrategy(bt.Strategy):  
  def __init__(self):
    self.dataclose = self.datas[0].close
    self.datetime = self.datas[0].datetime
    self.order = None

    self.takeProfit = None
    self.stopLoss = None
    
    # Indicadores
    self.ema20 = bt.indicators.ExponentialMovingAverage(self.dataclose, period=20)
    self.ema200 = bt.indicators.ExponentialMovingAverage(self.dataclose, period=200)
    self.macd = bt.indicators.MACD(self.dataclose)
    self.rsi =  bt.indicators.RSI(self.dataclose, period=14)
    self.crossover_macd_signal = bt.indicators.CrossOver(self.macd.macd, self.macd.signal, plotname='crossover macd/signal')
  
  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def next(self):

    # Cuando no tengo posición
    if self.position.size == 0:

      # Condiciones
      macd_enter = self.crossover_macd_signal > 0 and self.macd.macd < 0 # Posible cambio de tendencia
      rsi_positive = self.rsi > 50 # Tendencia alcista fuerte
      close_above_ema20 = self.dataclose > self.ema20  # Tendencia alcista en corto plazo
      close_above_ema200 = self.dataclose > self.ema200 # Tendencia alcista en largo plazo

      if macd_enter and rsi_positive and close_above_ema20 and close_above_ema200: 
          size = self.broker.getcash()/2/self.dataclose[0] # Invierto la mitad del capital
          self.log('BUY CREATE, %.2f' % self.dataclose[0])
          self.order = self.buy(size=size)

    # Cuando estoy comprado
    elif self.position.size > 0:
      
      # Condiciones
      close_below_ema200 = self.dataclose < self.ema200 # El precio en zona bajista de largo plazo
      macd_exit = self.crossover_macd_signal < 0 and self.macd.macd > 0 # Posible cambio de tendencia a la baja
      rsi_overbought = self.rsi > 70 # Indica sobrecompra del activo

      if close_below_ema200 or macd_exit or rsi_overbought:
        self.log('STOP LOSS HIT, SELL CREATE, %.2f' % self.dataclose[0])
        self.order = self.sell(size=self.position.size)
        

  def notify_order(self, order):
    
    # Enviada
    if order.status in [order.Submitted]:
      self.log('ORDER SUBMITTED')
      return
    
    # Aceptada
    if order.status in [order.Accepted]:
      self.log('ORDER ACCEPTED')
      return
    
    # Completada
    if order.status in [order.Completed]:
      if order.isbuy():
        self.log('BUY EXECUTED, %.2f' % order.executed.price)
      elif order.issell():
        self.log('SELL EXECUTED, %.2f' % order.executed.price)
        self.order = None

    # Cancelada, Margen insuficiente o Rechazada
    if order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')
      self.order = None

  def notify_trade(self, trade):
    if trade.isclosed:
      self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))
