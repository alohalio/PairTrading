import pandas as pd
import numpy as np
from visualization import Plot

def backtest(data: pd.DataFrame, pairs: list, ratio: list, fees: float=.1, slippage: float=.1,
             lookback: int=5, zscore_threshold: float=1.0):
    
    # Account retails commission fees and simple slippage
    FEE = fees / 100
    SLIPPAGE = slippage / 100

    for _ in range(len(pairs)//2):
        symbol_1, symbol_2 = pairs[2*_], pairs[2*_+1]
        beta = ratio[_]

        # Calcutate spread by using log price of asset A - (beta(hedge ratio) * log price of asset B)
        spread = np.log(data[symbol_1]) - beta * np.log(data[symbol_2])
        # Calculate zscore by using (spread - lagged spread mean) / lagged spread std to prevent lookahead bias
        zscore_column = f'({symbol_1}, {symbol_2})_zscore'
        data[zscore_column] = ((spread - spread.rolling(window=lookback).mean()) /
                               spread.rolling(window=lookback).std())
        
        upper_threshold, lower_threshold = zscore_threshold, -zscore_threshold

        position_column = f'({symbol_1}, {symbol_2})_position'
        # Entry long position asset A and short position asset B when zscore > upperthreshold
        data[position_column] = (data[zscore_column] > upper_threshold).astype(int)

        # Entry short position asset A and long position asset B when zscore < lowerthreshold
        data[position_column] = np.where(data[zscore_column] < lower_threshold, -1, data[position_column])

        # Calculate each symbol percentage change
        symbol_1_pct_column, symbol_2_pct_column = f'{symbol_1}_pct', f'{symbol_2}_pct'
        data[symbol_1_pct_column] = data[symbol_1].pct_change(periods=1).fillna(0)
        data[symbol_2_pct_column] = data[symbol_2].pct_change(periods=1).fillna(0)

        pair_pct = data[position_column].shift(periods=1).fillna(0) * (data[symbol_1_pct_column] - beta * data[symbol_2_pct_column])

        # Since we assuming that we diversify portfolio equal weight and entry 2 asset with different position at the same time
        # So we double transaction costs to estimate simple version of these transaction costs
        include_fees_pct = np.where(data[position_column].shift(periods=2).fillna(0) != data[position_column].shift(periods=1).fillna(0),
                                    pair_pct - 2 * FEE, pair_pct)
        include_fee_n_slippage_pct = np.where(data[position_column].shift(periods=2).fillna(0) != data[position_column].shift(periods=1).fillna(0),
                                              pair_pct - 2 * (FEE + SLIPPAGE), pair_pct)
        

        data[f'({symbol_1}, {symbol_2})_benchmark'] = ((1 + data[symbol_1_pct_column] + beta * data[symbol_2_pct_column]).cumprod() - 1) * 100
        data[f'({symbol_1}, {symbol_2})_exclude_fees_n_slippage'] = ((1 + pair_pct).cumprod() - 1) * 100
        data[f'({symbol_1}, {symbol_2})_include_fees'] = ((1 + include_fees_pct).cumprod() - 1) * 100
        data[f'({symbol_1}, {symbol_2})_include_fees_n_slippage'] = ((1 + include_fee_n_slippage_pct).cumprod() - 1) * 100
        

    plot = Plot(data, pairs)
    plot.plot_zscore()
    plot.plot_pnl()