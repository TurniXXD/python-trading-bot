import numpy as np
class ParticleMultidimensionalReplicator(QCAlgorithm):

    def Initialize(self):
        # account balance
        self.SetCash(100000)
        
        self.SetStartDate(2017,9,1)
        self.SetEndDate(2020,9,1)
        
        # trading symbol, using daily data
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        # number of days to lookback, algorithm will change lookback depends on volatility
        self.lookback = 20
        
        # upper and lower limit for lookback
        self.ceiling, self.floor = 30, 10
        
        # it alows 2% lost before it gets hit
        self.initialStopRisk = 0.98
        
        # Trail price by 10%
        self.trailingStopRisk = 0.9
        
        # method is called everyday, which time method is called (20 min after market is open), which method is called
        self.Schedule.On(self.DataRules.EveryDay(self.Symbol), \
                        self.TimeRules.AfterMarketOpen(self.symbol, 20), \
                        Action(self.EveryMarketOpen))

    def OnData(self, data):
        
        # name of the chart, name of the plot of the chart, data on the plot, data will be security closing price
        self.Plot("Data Chart", self.symbol, self.Securities[self.symbol].Close)
        
    def EveryMarketOpen(self):
        # determine loopback length and compare it for same value 
        
        # returns close, high, low, and open price, volume and price for past 31 days (for this case only close price will be returned)
        close = self.History(self.symbol, 31, Resolution.Daily)["close"]
        
        # numpy standart deviation function, first we do it for the current day and then for day before thats
        todayvol = np.std(close[1:31])
        yesterdayvol = np.std(close[0:30])
        
        # get normalized difference by subtracting yesterday value from to today and then dividing by today's value
        deltavol = (todayvol - yesterdayvol) / todayvol
        
        # multiply current lookback length by delta val + 1, this ensures that our lookback length increases when volatility increases and vice versa,
        # then we round our result to the neares integer
        self.lookback = round(self.lookback * (1 + deltavol))
        
        # check if our previously defined lookback is within upper and lower limits, if it isn't we make sure it is and otherwise do nothing
        if self.lookback > self.ceiling:
            self.lookback = self.ceiling
        elif self.lookback < self.floor:
            self.lookback = self.floor
            
        # Check whether breakout is happening, for this we call history function again to get a list of all daily price highs from the period within our lookback length
        self.high = self.History(self.symbol, self.lookback, Resolution.Daily)["high"]
        
        # check if aren't already investing and then if breakout is really happening, for breakout check if it's higher then the highest high from self.high
        # [:-1] means that we leave out the last data point of self.high because we don't want to compare yesterady's high with yesterday's close
        # if both conditions are met we will buy with SetHoldings, second argument is percentage of portfolio allocated for this position (now set to 100%)
        # save the breakoutlvl 
        # set var HighestPrice to breakoutlvl and then use it for trailing stop loss
        if not self.Securities[self.symbol].Invested and \
                self.Securities[self.symbol].Close >= max(self.high[:-1]):
                    self.SetHoldings(self.symbol, 1)
                    self.breakoutlvl = max(self.high[:-1])
                    self.highestPrice = self.breakoutlvl
        
        # implement trailing stop loss
        
        # check if don't already have open position if we already have open position trailing stop loss won't work
        # if not we send out stop loss with stop market order (takes 3 args), 1. symbol, 2. number of shares (-self = sell order), 3. stop loss price
        if self.Securities[self.symbol].Invested:
            if not self.Transactions.GetOpenOrders(self.symbol):
                self.stopMarketTicket = self.StopMarketOrder(self.symbol, \
                                        -self.Portfolio[self.symbol].Quantity, \
                                        self .initialStopRisk * self.breakoutlvl)
            
            # determine whether a new high has been made
            # test trailing stop loss to don't move below the initial stop loss price
            # set the highest price to the latest lowest price since this is the new highest price
            # create update order fields objec, updates price of stop loss so it rises with the securities price
            if self.Securities[self.symbol].Close > self.highestPrice and \
                    self.initialStopRisk * self.breakoutlvl < self.Securities[self.symbol].Close * self.trailingStopRisk:
                self.highestPrice = self.Securities[self.symbol].Close
                updateFields= UpdateOrderFields()
                updateFields.StopPrice = self.Securities[self.symbol].Close * self.trailingStopRisk
                self.stopMarketTicket.Update(updateFields)
                
                # print stop price to the console
                self.Debug(updateFields.StopPrice)
                
            # plot the stop price of our position onto the data chart
            self.Plot("Data Chart", "Stop Price", self.stopMarketTicket.Get(OrderField.StopPrice))