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
    def allStocks(conn): 
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
