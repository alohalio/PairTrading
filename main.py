import warnings
import numpy as np
from fetching import fetch_universe_data
from statsmodelling import cointegration, calc_beta
from backtest import backtest

warnings.filterwarnings('ignore')

universe = fetch_universe_data(limit=365)

# Drop high correlate asset to BTC and ETH
corr_data = np.log(1 + universe.pct_change()).corr()
high_corr = corr_data[((corr_data['BTC/USDT'] >= .95) & (corr_data['BTC/USDT'] < 1.0)) |
                      ((corr_data['ETH/USDT'] >= .95) & (corr_data['ETH/USDT'] < 1.0))].index.tolist()

universe = universe.drop(columns=high_corr, axis=1).fillna(method='bfill')
universe_columns = universe.columns.tolist()

cointegrate_data = cointegration(universe, universe_columns)

example_pairs = ['BTC/USDT', 'TRX/USDT',
                 'SOL/USDT', 'RAY/USDT',
                 'DOT/USDT', 'JTO/USDT',
                 'ADA/USDT', 'XLM/USDT',
                 'BNB/USDT', 'AAVE/USDT']

print(cointegrate_data[((cointegrate_data['symbol_1'] == example_pairs[0]) & (cointegrate_data['symbol_2'] == example_pairs[1])) |
                       ((cointegrate_data['symbol_1'] == example_pairs[2]) & (cointegrate_data['symbol_2'] == example_pairs[3])) |
                       ((cointegrate_data['symbol_1'] == example_pairs[4]) & (cointegrate_data['symbol_2'] == example_pairs[5])) |
                       ((cointegrate_data['symbol_1'] == example_pairs[6]) & (cointegrate_data['symbol_2'] == example_pairs[7])) |
                       ((cointegrate_data['symbol_1'] == example_pairs[8]) & (cointegrate_data['symbol_2'] == example_pairs[9]))])

pair_data = universe.loc[:, universe.columns.isin(example_pairs)]

beta_ratio = calc_beta(pair_data, example_pairs)

backtest(data=pair_data, pairs=example_pairs, ratio=beta_ratio)