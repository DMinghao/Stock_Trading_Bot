import alpaca_trade_api as tradeapi
import threading
import time
import datetime
from tradingview_ta import TA_Handler, Interval

from .constant import alpaca, rating

class util: 
    """This util class provides handy tools 
    
    
    """
    @staticmethod
    def connectAlpaca(): 
        """Returns an Alpaca connection object
            the connection object allows user to operate on thier Alpaca account 
        """
        print("Conneting...")
        return tradeapi.REST(
            key_id=alpaca.APCA_API_KEY_ID, 
            secret_key=alpaca.APCA_API_SECRET_KEY, 
            base_url=alpaca.APCA_API_PAPER_BASE_URL, 
            api_version='v2')

    @staticmethod
    def allStocks(conn=connectAlpaca.__func__): 
        """Get all tradeable stocks by rating
        """
        universe = conn.list_assets(status='active', asset_class='us_equity')
        universe = [{'exchange':x.exchange, 'symbol':x.symbol} for x in universe if x.shortable == True and x.tradable == True]
        
        def getSummary(i): 
            handler = TA_Handler()
            handler.set_screener_as_stock("america")
            handler.set_interval_as(Interval.INTERVAL_1_DAY)
            handler.set_exchange_as_crypto_or_stock(universe[i]['exchange'])
            handler.set_symbol_as(universe[i]['symbol'])
            try:
                universe[i]['rating'] = handler.get_analysis().summary
            except: 
                pass
        
        threads = []
        for i in range(len(universe)):
            x = threading.Thread(target=getSummary, args=(i,))
            threads.append(x)
            x.start()
        for thread in threads: 
            thread.join()
        buyList = [
            x for x in universe 
            if 'rating' in x 
            and x['rating']['RECOMMENDATION'] == rating.BUY
        ]
        buyList.sort(key=lambda x: x['rating'][rating.BUY], reverse = True)
        buyStrongList = [
            x for x in universe 
            if 'rating' in x 
            and x['rating']['RECOMMENDATION'] == rating.STRONG_BUY
        ]
        buyStrongList.sort(key=lambda x: x['rating'][rating.BUY], reverse = True)
        nutrualList = [
            x for x in universe 
            if 'rating' in x 
            and x['rating']['RECOMMENDATION'] == rating.NEUTRAL
        ]
        nutrualList.sort(key=lambda x: x['rating'][rating.NEUTRAL], reverse = True)
        sellList = [
            x for x in universe 
            if 'rating' in x 
            and x['rating']['RECOMMENDATION'] == rating.SELL
        ]
        sellList.sort(key=lambda x: x['rating'][rating.SELL], reverse = True)
        sellStrongList = [
            x for x in universe 
            if 'rating' in x 
            and x['rating']['RECOMMENDATION'] == rating.STRONG_SELL
        ]
        sellStrongList.sort(key=lambda x: x['rating'][rating.SELL], reverse = True)
        return {'STRONG_BUY':buyStrongList,'BUY':buyList,'NEUTRAL':nutrualList,'SELL':sellList, 'STRONG_SELL':sellStrongList}

    @staticmethod
    def awaitMarketOpen(conn=connectAlpaca.__func__):
        isOpen = conn.get_clock().is_open
        while(not isOpen):
            clock = conn.get_clock()
            openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)
            print(str(timeToOpen) + " minutes til market open.")
            time.sleep(60)
            isOpen = conn.get_clock().is_open

    @staticmethod
    def getTotalPrice(stocks, result=['DEFAULT'], conn=connectAlpaca.__func__):
        totalPrice = 0
        for stock in stocks:
            bars = conn.get_barset(stock, "minute", 1)
            totalPrice += bars[stock][0].c
        if result[0] == 'DEFAULT': 
            return totalPrice
        else: result.append(totalPrice)

    @staticmethod
    def getPercentChanges(stocks, timeInterval=10, conn=connectAlpaca.__func__):
        length = timeInterval
        for i, stock in enumerate(stocks): 
            bars = conn.get_barset(stock[0], 'minute', length)
            stocks[i][1] = (bars[stock[0]][len(bars[stock[0]]) - 1].c - bars[stock[0]][0].o) / bars[stock[0]][0].o

    @staticmethod
    def submitOrder(qty, stock, side, result=['DEFAULT'], conn=connectAlpaca.__func__):
        completed = False
        if(qty > 0):
            try:
                conn.submit_order(stock, qty, side, "market", "day")
                print("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
                completed = True
            except:
                print("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
                completed = False
        else:
            print("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
            completed = True
        if result[0] == 'DEFAULT': 
            return completed
        else: result.append(completed)
    
    @staticmethod
    def sendBatchOrder(qty, stocks, side, blacklist=[], result=['DEFAULT'], conn=connectAlpaca.__func__):
        executed = []
        incomplete = []
        for stock in stocks:
            if(blacklist.isdisjoint({stock})):
                respSO = []
                tSubmitOrder = threading.Thread(target=submitOrder.__func__, args=[qty, stock, side, respSO, conn])
                tSubmitOrder.start()
                tSubmitOrder.join()
                if(not respSO[0]):
                    # Stock order did not go through, add it to incomplete.
                    incomplete.append(stock)
                else:
                    executed.append(stock)
                respSO.clear()
        if result[0] == 'DEFAULT': 
            return [executed, incomplete]
        else: result.append([executed, incomplete])

if __name__ == '__main__': 
    print('Start Testing Util: ')
    import unittest
