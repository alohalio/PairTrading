# Pair Trading Project

## Overview

This project implements a simple pair trading strategy using cryptocurrency data from the Binance exchange. Pair trading is a market-neutral strategy that involves identifying two highly correlated assets and trading based on their price divergence. The project fetches historical price data, performs cointegration analysis to identify tradable pairs, calculates hedge ratios (β), conducts a simple backtest of the trading strategy, and generates dynamic visualizations to evaluate performance.

## Project Structure

The project is organized into the following Python files:
- main.py: Orchestrates the workflow, including data fetching, cointegration analysis, beta calculation, and backtesting.
- fetching.py: Retrieves historical price data from Binance using the CCXT library, focusing on USDT-quoted spot market pairs with high liquidity.
- statsmodelling.py: Performs cointegration testing and calculates hedge ratios using statistical methods.
- backtest.py: Implements the pair trading strategy, calculates z-scores, determines positions, and computes performance metrics, including fees and slippage.
- visualization.py: Generates interactive plots for z-scores and cumulative returns using Plotly.

## Dataset

The project uses daily candlestick data from the Binance exchange, sourced via the CCXT library. The sample period spans from June 19 2024, to June 18 2025, providing 365 days of data for quick evaluation.

## Data Processing

### Filtering Data

To align with real-world trading scenarios, the data is filtered as follows:
- Market and Quote Selection: Only spot market pairs quoted in USDT with active status are included to exclude inactive or irrelevant instruments.
- Liquidity Filter: The top 100 pairs by 24-hour trading volume are selected to ensure sufficient liquidity.
- Correlation Filter: Assets with a correlation of ≥ 0.95 to BTC or ETH (based on the natural log of percentage changes) are excluded to avoid pairs that move too closely with major cryptocurrencies.

### Statistical Modelling

#### Cointegration

The Statsmodels library is used to perform the Engle-Granger cointegration test. Pairs with a p-value < 0.05 (95% confidence level) are selected, rejecting the null hypothesis that the spread between the pair diverges significantly over time.

#### Beta(β) Calculation

Hedge ratios (β) are calculated using Ordinary Least Squares (OLS) regression on the natural log of closing prices for each pair. The first 80% of the data is used as the training period to determine the beta for instrument B relative to instrument A.

## Trading Strategy

The strategy focuses on five example pairs with sufficient data points within the sample period. The selected pairs and their cointegration p-values are:

| Symbol 1 | Symbol 2 | P-Value |
| --- | --- | --- |
| BTC/USDT | TRX/USDT | 0.001950 |
| SOL/USDT | RAY/USDT | 0.031426 |
| BNB/USDT | AAVE/USDT | 0.025709 |
| ADA/USDT | XLM/USDT | 0.000018 |
| DOT/USDT | JTO/USDT | 0.035420 |

### Strategy Logic

Spread Calculation: log(Instrument A) - β x log(Instrument B)

Z-Score Calculation: (Spread- Spread.rolling(lookback).mean()) / Spread.rolling(lookback).std()
The default lookback period is 5 days, to avoid lookahead bias, the z-score is computed using a rolling mean and standard deviation.

#### Each Pair's Z-Score
![Each Pair's Z-Score](https://github.com/alohalio/PairTrading/blob/main/pics/zscore.png)

Entry and Exit Rules:
- Long Entry: Enter a long position in Instrument A and a short position in Instrument B when the z-score > upper threshold (default: +1.0).
- Short Entry: Enter a short position in Instrument A and a long position in Instrument B when the z-score < lower threshold (default: -1.0).
- Exit: Close positions when the z-score crosses back within the thresholds (default ±1.0).

## Backtesting

The backtest evaluates the strategy's performance while accounting for transaction costs (0.1% commission fees and 0.1% slippage) to simulate real-world conditions. The gross profit is calculated as:[\text{Gross Profit} = \text{Position}{t-1} \cdot (\text{Instrument A % change} - \beta \cdot \text{Instrument B % change})]To account for transaction costs, the net profit adjusts for fees and slippage when positions change:[\text{Net Profit} =\begin{cases}\text{Gross Profit} - 2 \cdot (\text{Fees} + \text{Slippage}), & \text{if } \text{Position}{t-1} \neq \text{Position}_{t-2} \\text{Gross Profit}, & \text{otherwise}\end{cases}]The factor of 2 accounts for trading two assets simultaneously in pair trading. The backtest uses close price data, ensuring signals are based on the previous period's close to avoid lookahead bias.

The backtest outputs four performance metrics for each pair:
- Benchmark: Cumulative returns of holding both assets (Instrument A + β × Instrument B).
- Strategy (Exclude Fees & Slippage): Cumulative returns without transaction costs.
- Strategy (Include Fees): Cumulative returns with commission fees.
- Strategy (Include Fees & Slippage): Cumulative returns with both fees and slippage.

### Results

#### BTC/TRX Benchmark vs Strategy Cumulative Returns
![BTC/TRX Benchmark vs Strategy Cumulative Returns](https://github.com/alohalio/PairTrading/blob/main/pics/btc_trx.png)

#### SOL/RAY Benchmark vs Strategy Cumulative Returns
![SOL/RAY Benchmark vs Strategy Cumulative Returns](https://github.com/alohalio/PairTrading/blob/main/pics/sol_ray.png)

#### BNB/AAVE Benchmark vs Strategy Cumulative Returns
![BNB/AAVE Benchmark vs Strategy Cumulative Returns](https://github.com/alohalio/PairTrading/blob/main/pics/bnb_aave.png)

#### ADA/XLM Benchmark vs Strategy Cumulative Returns
![ADA/XLM Benchmark vs Strategy Cumulative Returns](https://github.com/alohalio/PairTrading/blob/main/pics/ada_xlm.png)

#### DOT/JTO Benchmark vs Strategy Cumulative Returns
![DOT/JTO Benchmark vs Strategy Cumulative Returns](https://github.com/alohalio/PairTrading/blob/main/pics/dot_jto.png)

## Visualization

The project generates two types of interactive plots using Plotly:
- Z-Score Plot: Displays the z-score for each pair over time.
- Cumulative Returns Plot: Compares the benchmark and strategy returns (with and without fees/slippage), with the out-of-sample period (last 20% of data) highlighted.

## Notes
- The default timeframe is daily (1d), with 365 days of data. Modify limit in fetch_universe_data to adjust.
- Transaction costs are set to 0.1% for both fees and slippage. Adjust in backtest.py as needed.
- The z-score threshold is ±1.0. Modify zscore_threshold in backtest.py to experiment with different sensitivities.
- Visualizations use the plotly_dark template and Noto Serif Kr font. Customize in visualization.py if desired.
- For realistic backtesting, consider using frameworks like Backtesting.py, Zipline, or VectorBT.
- To improve the strategy consider to applied fundamental/technical indicators, statistical model (e.g., Kalman Filter) or machine learning (e.g., Linear Regression).

## License
This project is licensed under the MIT License. See the LICENSE file for details.