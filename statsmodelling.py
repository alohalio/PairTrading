import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint

def cointegration(universe_data: pd.DataFrame, pairs_list: list, significance: float=.05, minimum_data_points: int=10):
    data = universe_data.copy()
    cointegrate_pairs = []
    
    for _ in range(len(pairs_list)):
        for __ in range(_ + 1, len(pairs_list)):
            symbol_1, symbol_2 = pairs_list[_], pairs_list[__]

            series_1, series_2 = data[symbol_1], data[symbol_2]

            if len(series_1) < minimum_data_points or len(series_2) < minimum_data_points:
                print(f'Skipping pair ({symbol_1}, {symbol_2}) due to insufficient data points')
                continue

            try:
                t_stat, p_value, c_value = coint(series_1, series_2)
                is_cointegrated = p_value < significance # Default significance at 0.5% to reject null-hypothesis

                if is_cointegrated:
                    cointegrate_pairs.append({
                        'symbol_1': symbol_1,
                        'symbol_2': symbol_2,
                        'p_value': p_value
                    })
                else:
                    pass
            except Exception as e:
                print(f'Error testing pair ({symbol_1}, {symbol_2}): {e}')
                continue

    return pd.DataFrame.from_dict(cointegrate_pairs)

def calc_beta(data: pd.DataFrame, pairs_selected: list):
    beta_stacks = []

    # Determine beta based on train data periods
    train_data = data.copy()
    train_data = train_data.iloc[:int(len(train_data) * .8)]

    for _ in range(len(pairs_selected)//2):
        symbol_1, symbol_2 = pairs_selected[2*_], pairs_selected[2*_+1]
        x, y = np.log(train_data[symbol_2]), np.log(train_data[symbol_1])
        x = sm.add_constant(x)

        model = sm.OLS(y, x)
        result = model.fit()

        beta_stacks.append(result.params[1])
    
    return beta_stacks