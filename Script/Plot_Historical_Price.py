# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 12:10:24 2025

@author: u0156396
"""


import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo

def plot_currency(currency, title="Exchange Rate History"):
    traces = []
    color_map = {
        "Cash_Buy": 'blue',
        "Cash_Sell": 'blue',
        "Spot_Buy": 'rgba(255,0,0,0.7)',
        "Spot_Sell": 'rgba(255,0,0,0.7)',
    }
    line_map = {
        "Buy": 'solid',
        "Sell": 'dashdot',
    }
    for t in ['Cash', 'Spot']:
        csv_file = f'../Data/Historical Download/{currency}_{t}_Historical.csv'
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df['DateStr'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        df['MA20'] = df['Buying'].rolling(5).mean()
        df['EMA20'] = df['Buying'].ewm(span=5).mean()
        traces.append(go.Scatter(
            x=df['Date'], y=df['EMA20'],
            mode='lines', name=f'{t} Buying',
            line=dict(
                width=3,
                color=color_map[f"{t}_Buy"],
                dash=line_map['Buy']
            ),
            hovertemplate=None, hoverinfo='skip'
        ))

        df['MA20'] = df['Selling'].rolling(5).mean()
        df['EMA20'] = df['Selling'].ewm(span=5).mean()
        traces.append(go.Scatter(
            x=df['Date'], y=df['EMA20'],
            mode='lines', name=f'{t} Selling',
            line=dict(
                width=3,
                color=color_map[f"{t}_Sell"],
                dash=line_map['Sell']
            ),
            hovertemplate=None, hoverinfo='skip'
        ))

        # 打點，但是不顯示，只顯示數值
        traces.append(go.Scatter(
            x=df['Date'], y=df['Buying'],
            customdata=df['DateStr'],
            hovertemplate='日期：%{customdata}<br>買入：%{y:.4f}<extra></extra>',
            mode='markers', name=f'{t} Buying', showlegend=False,
            marker=dict(size=6, color='rgba(0,0,0,0)')
        ))
        traces.append(go.Scatter(
            x=df['Date'], y=df['Selling'],
            customdata=df['DateStr'],
            mode='markers', name=f'{t} Selling', showlegend=False,
            marker=dict(size=6, color='rgba(0,0,0,0)')
        ))
    endtime   = df.loc[df.index.stop-1,"Date"]+pd.Timedelta(hours=24)
    starttime = endtime-pd.Timedelta(hours=365*24)
    layout = go.Layout(
        xaxis=dict(
            title='Date',
            range=[starttime, endtime],      # 只影響初始視窗範圍
            showgrid=True,
            gridcolor='#ddd',
            tickformat='%Y-%m',              # x軸標籤顯示年月
            dtick='M1',                      # 一個月一格
            rangeslider=dict(
                visible=True,
                thickness=0.12,
                bgcolor="#f5f7fa",
                bordercolor="#bbb",
                borderwidth=1
            ),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
        ),
        yaxis=dict(
            title='Rate',
            showgrid=True,
            gridcolor='#ddd'
        ),
        hovermode='x unified',
        plot_bgcolor="#f5f7fa",
        margin=dict(l=10, r=10, t=10, b=10)
    )



    fig = go.Figure(data=traces, layout=layout)
    # fig.update_layout(
    #     updatemenus=[
    #         dict(
    #             type="buttons",
    #             direction="right",
    #             x=0.5, y=1.13, xanchor="center", yanchor="bottom",
    #             bgcolor='#eaf4fa',                   # 跟 rangeslider 一樣的淡藍色
    #             bordercolor='#bbb',
    #             borderwidth=1,
    #             font=dict(size=18, color='#19547b', family='Segoe UI, Arial, sans-serif'),
    #             pad=dict(l=18, r=18, t=12, b=12),    # 內邊距更大更厚
    #             buttons=[
    #                 dict(label="All", method="update",
    #                     args=[{"visible": [True]*8}]),
    #                 dict(label="Cash", method="update",
    #                     args=[{"visible": [True, True, True, True, False, False, False, False]}]),
    #                 dict(label="Spot", method="update",
    #                     args=[{"visible": [False, False, False, False, True, True, True, True]}])
    #             ],
    #             showactive=True,
    #         )
    #     ]
    # )
    fig.write_html(f"../Figure/plot_{currency}.html", full_html=True)
    with open(f"../Figure/plot_{currency}.html", "a", encoding="utf8") as f:
        f.write("""
    <script>
    window.addEventListener('resize', function() {
        Plotly.Plots.resize(document.querySelector('.js-plotly-plot'));
    });
    window.addEventListener('DOMContentLoaded', function() {
        Plotly.Plots.resize(document.querySelector('.js-plotly-plot'));
    });
    setTimeout(function(){
        Plotly.Plots.resize(document.querySelector('.js-plotly-plot'));
    }, 200);
    </script>
    """)


def plot_now(currency):
    traces = []
    color_map = {
        "Cash_Buy": 'rgba( 36,113,163,0.7)',
        "Cash_Sell": 'rgba(203, 67, 53,0.7)',
        "Spot_Buy": 'rgba(255,0,0,0.7)',
        "Spot_Sell": 'rgba(255,0,0,0.7)',
    }
    line_map = {
        "Buy": 'solid',
        "Sell": 'dashdot',
    }
    for t in ['Cash']:
        csv_file = f'../Data/history/{currency}.csv'
        df = pd.read_csv(csv_file)
        df.columns = ['Date',"Buying","Buying.1","Selling","Selling.1"]
        df['Date'] = pd.to_datetime(df['Date'])
        df['DateStr'] = df['Date'].dt.strftime('%Y/%m/%d %H:%M:%S')

        df['MA20'] = df['Buying'].rolling(3).mean()
        df['EMA20'] = df['Buying'].ewm(span=3).mean()
        traces.append(go.Scatter(
            x=df['Date'], y=df['EMA20'],
            mode='lines', name=f'{t} Buying',
            line=dict(
                width=3,
                color=color_map[f"{t}_Buy"],
                dash=line_map['Buy']
            ),
            hovertemplate=None, hoverinfo='skip'
        ))

        df['MA20'] = df['Selling'].rolling(3).mean()
        df['EMA20'] = df['Selling'].ewm(span=3).mean()
        traces.append(go.Scatter(
            x=df['Date'], y=df['EMA20'],
            mode='lines', name=f'{t} Selling',
            line=dict(
                width=3,
                color=color_map[f"{t}_Sell"],
                dash=line_map['Sell']
            ),
            hovertemplate=None, hoverinfo='skip'
        ))

        # 打點，但是不顯示，只顯示數值
        traces.append(go.Scatter(
            x=df['Date'], y=df['Buying'],
            customdata=df['DateStr'],
            hovertemplate='Date：%{customdata}<br>Buying：%{y:.4f}<extra></extra>',
            mode='markers', name=f'{t} Buying', showlegend=False,
            marker=dict(size=6, color='rgba( 26, 82,118,1.0)')
        ))
        traces.append(go.Scatter(
            x=df['Date'], y=df['Selling'],
            customdata=df['DateStr'],
            mode='markers', name=f'{t} Selling', showlegend=False,
            marker=dict(size=6, color='rgba(148, 49, 38,1.0)')
        ))
    endtime   = df.loc[df.index.stop-1,"Date"]+pd.Timedelta(hours=24)
    starttime = endtime-pd.Timedelta(hours=365*24)
    layout = go.Layout(
        xaxis=dict(
            title='Date',
            range=[starttime, endtime],      # 只影響初始視窗範圍
            showgrid=True,
            gridcolor='#ddd',
            tickformat='%Y-%m',              # x軸標籤顯示年月
            dtick='M1',                      # 一個月一格
            rangeslider=dict(
                visible=True,
                thickness=0.12,
                bgcolor="#f5f7fa",
                bordercolor="#bbb",
                borderwidth=1
            ),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
        ),
        yaxis=dict(
            title='Rate',
            showgrid=True,
            gridcolor='#ddd'
        ),
        hovermode='x unified',
        plot_bgcolor="#f5f7fa",
        margin=dict(l=10, r=10, t=10, b=10)
    )



    fig = go.Figure(data=traces, layout=layout)
    # fig.update_layout(
    #     updatemenus=[
    #         dict(
    #             type="buttons",
    #             direction="right",
    #             x=0.5, y=1.13, xanchor="center", yanchor="bottom",
    #             bgcolor='#eaf4fa',                   # 跟 rangeslider 一樣的淡藍色
    #             bordercolor='#bbb',
    #             borderwidth=1,
    #             font=dict(size=18, color='#19547b', family='Segoe UI, Arial, sans-serif'),
    #             pad=dict(l=18, r=18, t=12, b=12),    # 內邊距更大更厚
    #             buttons=[
    #                 dict(label="All", method="update",
    #                     args=[{"visible": [True]*8}]),
    #                 dict(label="Cash", method="update",
    #                     args=[{"visible": [True, True, True, True, False, False, False, False]}]),
    #                 dict(label="Spot", method="update",
    #                     args=[{"visible": [False, False, False, False, True, True, True, True]}])
    #             ],
    #             showactive=True,
    #         )
    #     ]
    # )
    fig.write_html(f"../Figure/plot_now_{currency}.html", full_html=True)
    # with open(f"../Figure/plot_now_{currency}.html", "a", encoding="utf8") as f:
    #     f.write("""
    # <script>
    # window.addEventListener('resize', function() {
    #     Plotly.Plots.resize(document.querySelector('.js-plotly-plot'));
    # });
    # window.addEventListener('DOMContentLoaded', function() {
    #     Plotly.Plots.resize(document.querySelector('.js-plotly-plot'));
    # });
    # setTimeout(function(){
    #     Plotly.Plots.resize(document.querySelector('.js-plotly-plot'));
    # }, 200);
    # </script>
    # """)

if __name__ =="__main__":
    for currency in ["USD","JPY","EUR","CNY"]:
        plot_currency(currency, title=f"{currency} Cash/Spot Buying/Selling Rate")