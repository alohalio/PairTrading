import pandas as pd
import plotly.graph_objects as go


class Plot:
    def __init__(self, data: pd.DataFrame, pairs: list):
        self.data = data
        self.pairs = pairs

    def plot_zscore(self):
        fig = go.Figure()

        for _ in range(len(self.pairs)//2):
            symbol_1, symbol_2 = self.pairs[2*_], self.pairs[2*_+1]
            zscore_column = f'({symbol_1}, {symbol_2})_zscore'

            fig.add_trace(go.Scatter(x=self.data.index,
                                     y=self.data[zscore_column],
                                     name=f'({symbol_1}, {symbol_2})'))
    
        fig.update_layout(
            title=f"Each Pair's ZScore",
            font_family='Noto Serif Kr',
            xaxis_title='Date',
            yaxis_title='Zscore',
            template='plotly_dark'
        )

        fig.show()
    
    def plot_pnl(self):
        for _ in range(len(self.pairs)//2):
            fig = go.Figure()
            symbol_1, symbol_2 = self.pairs[2*_], self.pairs[2*_+1]

            pair = f'({symbol_1}, {symbol_2})'

            fig.add_trace(go.Scatter(x=self.data.index,
                                     y=self.data[f'{pair}_benchmark'],
                                     name='Benchmark'))
            
            fig.add_trace(go.Scatter(x=self.data.index,
                                     y=self.data[f'{pair}_exclude_fees_n_slippage'],
                                     name='Strategy exclude fees & slippage'))
            
            fig.add_trace(go.Scatter(x=self.data.index,
                                     y=self.data[f'{pair}_include_fees'],
                                     name='Strategy include fees'))
            
            fig.add_trace(go.Scatter(x=self.data.index,
                                     y=self.data[f'{pair}_include_fees_n_slippage'],
                                     name='Strategy include fees & slippage'))
            
            fig.add_vrect(x0=self.data.index[int(len(self.data)*.8)+1],
                          x1=self.data.index[-1],
                          fillcolor='lightgray',
                          opacity=0.3,
                          layer='below',
                          annotation_text='Out-of-sample',
                          annotation_position='top left')
            
            fig.update_layout(
                title=f'{pair} Benchmark vs Strategy Cumulative Returns',
                font_family='Noto Serif Kr',
                xaxis_title='Date',
                yaxis_title='PnL(%)',
                template='plotly_dark'
            )

            fig.show()