# Plot 
import pandas as pd
import plotly.graph_objs as go
import plotly.offline    as pyo
from utils.config import CURRENCIES

def plot_history(
    csv_file_path,
    currency,
    title="Exchange Rate History",
    show_html: bool = False,
    save_html: bool = False,
    save_directory=None
):
    traces = []

    color_map = {
        "Cash_Buy": 'blue',
        "Cash_Sell": 'blue',
        "Spot_Buy": 'rgba(255,0,0,0.7)',
        "Spot_Sell": 'rgba(255,0,0,0.7)',
    }
    line_map = {"Buy": "solid", "Sell": "dashdot"}

    # 你原本每次 loop 讀一次 csv，這裡讀一次就好
    for t in ["Cash", "Spot"]:
        df = pd.read_csv(csv_file_path.format(currency=currency, t=t))
        df["Date"] = pd.to_datetime(df["Date"])
        df["DateStr"] = df["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        # ===== 趨勢線（EMA）：只畫，不參與 hover =====
        df["EMA_Buy"] = df[f"{t}"].ewm(span=5).mean()
        traces.append(go.Scatter(
            x=df["Date"], y=df["EMA_Buy"],
            mode="lines",
            name=f"{t} Buying",
            line=dict(width=3, color=color_map[f"{t}_Buy"], dash=line_map["Buy"]),
            hoverinfo="skip"  # ✅ 線不顯示 hover
        ))

        df["EMA_Sell"] = df[f"{t}.1"].ewm(span=5).mean()
        traces.append(go.Scatter(
            x=df["Date"], y=df["EMA_Sell"],
            mode="lines",
            name=f"{t} Selling",
            line=dict(width=3, color=color_map[f"{t}_Sell"], dash=line_map["Sell"]),
            hoverinfo="skip"  # ✅ 線不顯示 hover
        ))

        # ===== 隱藏點：不顯示，但承載 hover（顯示原始值）=====
        # 買入點（隱形）
        traces.append(go.Scatter(
            x=df["Date"], y=df[f"{t}"],
            mode="markers",
            name=f"{t} Buying (raw)",
            showlegend=False,
            marker=dict(size=10, color="rgba(0,0,0,0)"),  # ✅ 點透明但可 hover
            customdata=df["DateStr"],
            hovertemplate=f"{t} <br>   Buying: %{{y:.4f}}<extra></extra>"
        ))

        # 賣出點（隱形）
        traces.append(go.Scatter(
            x=df["Date"], y=df[f"{t}.1"],
            mode="markers",
            name=f"{t} Selling (raw)",
            showlegend=False,
            marker=dict(size=10, color="rgba(0,0,0,0)"),
            customdata=df["DateStr"],
            hovertemplate="   Selling: %{y:.4f}<extra></extra>"
        ))

    endtime = df["Date"].iloc[-1] + pd.Timedelta(hours=24)
    starttime = endtime - pd.Timedelta(days=90)

    layout = go.Layout(
        showlegend=False,  # ✅ 全局關閉 legend
        xaxis=dict(
            title="Date",
            range=[starttime, endtime],
            hoverformat='%Y-%m-%d %H:%M:%S',
            showgrid=True,
            gridcolor="#ddd",
            tickformat="%Y-%m",   # ✅ x 軸只顯示年月
            dtick="M1",
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
        yaxis=dict(title="Rate", showgrid=True, gridcolor="#ddd"),
        hovermode="x unified",   # ✅ 同一個 x 一起顯示
        plot_bgcolor="#f5f7fa",
        margin=dict(l=10, r=10, t=40, b=10)
    )

    fig = go.Figure(data=traces, layout=layout)

    if show_html:
        fig.show()

    if save_html:
        if save_directory is None:
            save_directory = "../Figure"
        fig.write_html(save_directory, full_html=True)

    return fig


def plot_now(csv_file_path,currency,
             show_html: bool = False,
             save_html: bool = False,
             save_directory = None):
    traces = []
    color_map = {"Cash_Buy": 'rgba( 36,113,163,0.7)',
                 "Cash_Sell": 'rgba(203, 67, 53,0.7)',}
    line_map = {"Buy": 'solid', "Sell": 'dashdot'}

    df = pd.read_csv(csv_file_path)
    # df.columns = ['Date', "Cash", "Cash.1", "Selling", "Selling.1"]
    df['Date'] = pd.to_datetime(df['Date'])

    # ===== 線（EMA） =====
    df['EMA_Buy'] = df['Cash'].ewm(span=3).mean()
    traces.append(go.Scatter(
        x=df['Date'], y=df['EMA_Buy'],
        mode='lines',
        name='Cash Buying',
        line=dict(width=3, color=color_map["Cash_Buy"], dash=line_map['Buy']),
        hovertemplate=None, hoverinfo='skip'
    ))

    df['EMA_Sell'] = df['Cash.1'].ewm(span=3).mean()
    traces.append(go.Scatter(
        x=df['Date'], y=df['EMA_Sell'],
        mode='lines',
        name='Cash Selling',
        line=dict(width=3, color=color_map["Cash_Sell"], dash=line_map['Sell']),
        hovertemplate=None, hoverinfo='skip'
    ))

    # ===== Scatter(Original data) =====
    traces.append(go.Scatter(
        x=df['Date'], y=df['Cash'],
        mode='markers',
        name='Cash Buying',
        showlegend=False,
        marker=dict(size=6, color='rgba(26, 82,118,1.0)'),
        hovertemplate='Buying: %{y:.4f}<extra></extra>'
    ))
    traces.append(go.Scatter(
        x=df['Date'], y=df['Cash.1'],
        mode='markers',
        name='Cash Selling',
        showlegend=False,
        marker=dict(size=6, color='rgba(148, 49, 38,1.0)'),
        hovertemplate='Selling: %{y:.4f}<extra></extra>'
    ))

    endtime = df['Date'].iloc[-1] + pd.Timedelta(hours=24)
    starttime = endtime - pd.Timedelta(days=30)

    layout = go.Layout(
        xaxis=dict(
            title='Date',
            range=[starttime, endtime],
            showgrid=True,
            gridcolor='#ddd',
            tickformat='%Y-%m',
            dtick='M1',
            hoverformat='%Y-%m-%d %H:%M:%S',

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
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Segoe UI"
        ),

        plot_bgcolor="#f5f7fa",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )

    fig = go.Figure(data=traces, layout=layout)

    if show_html: fig.show()
    if save_html: fig.write_html(save_directory, full_html=True)

    return fig


def build_all_plots():
    for currency in CURRENCIES:
        csv_file = f'../Data/history/{currency}.csv'
        plot_now(csv_file,currency)
        csv_file = f'../Data/Historical Download/{currency}_{t}_Historical.csv'
        plot_currency(currency)

def to_html(save_directory,
            currency):
    with open(f"{save_directory}/plot_{currency}.html", "a", encoding="utf8") as f:
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

if __name__ =="__main__":
    build_all_plots()