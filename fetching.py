import ccxt
import pandas as pd
from datetime import datetime, timedelta

def fetch_universe_data(timeframe: str='1d', limit: int=30):
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })

    """ Filter only spot market and currently active symbol which quote by usdt """
    try:
        market = exchange.load_markets()
    except Exception as e:
        print(f'Error fetching market data: {e}')
        return []

    usdt_pairs = [symbol for symbol, market in market.items()
                  if market['quote'] == 'USDT' and market['spot']
                  and market['active']]
    
    """ Sorted top 100 24H volume to simple prevent low liquidity assets """
    try:
        ticker = exchange.fetch_tickers()
    except Exception as e:
        print(f'Error fetching tickers: {e}')
        return []
    
    ticker_data = []
    for symbol, ticker in ticker.items():
        if symbol in usdt_pairs and ticker\
            and ticker['quoteVolume'] is not None:

            ticker_data.append({
                'symbol': symbol,
                'liquidity': ticker['quoteVolume']
            })

    liquidity_sorted = sorted(ticker_data, key=lambda x: x['liquidity'], reverse=True)[:100]
    liquidity_symbol = [symbol['symbol'] for symbol in liquidity_sorted]

    """ Fetching daily historical candlestick data """
    ohlcv_data = {}
    timeframe = timeframe
    limit = limit
    start = int((datetime.now() - timedelta(days=limit)).timestamp() * 1000)
    
    for symbol in liquidity_symbol:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=start)
            ohlcv_data[symbol] = pd.DataFrame(ohlcv,
                                              columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            ohlcv_data[symbol]['timestamp'] = pd.to_datetime(ohlcv_data[symbol]['timestamp'], unit='ms')
            ohlcv_data[symbol] = ohlcv_data[symbol].set_index('timestamp')

        except Exception as e:
            print(f'Error fetching candlestick data for {symbol}: {e}')
            continue
    
    merge_data = pd.concat(ohlcv_data, axis=1)
    close_data = merge_data.loc[:, merge_data.columns.get_level_values(1).isin(['close'])]
    close_data.columns = close_data.columns.droplevel(1)
    
    return close_data