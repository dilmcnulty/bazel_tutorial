import plotly.graph_objects as go 
import pandas as pd 

splits = {
    'TSLA': ('2022-08-25', 3),
    'AMZN': ('2022-06-06', 20)
}

def build_chart(data: dict[str, list[tuple[str,float]]]): 
    clean_data = clean_splits(data)   
    
    df = pd.DataFrame(clean_data)
    df = df.reset_index(names='Date')
    
    chart = go.Figure()

    for ticker in clean_data.keys():
        chart.add_trace(go.Scatter(
            x=df['Date'],
            y=df[ticker],
            mode='lines',
            name=ticker
        ))

    chart.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        title="Stock Data",
        template="plotly_white"
    )

    return chart 

def clean_splits(data: dict[str, list[tuple[str,float]]]):
    # find datapoints prior to splits and divide their price by the 
    # split ratio for accurate comparison 
    clean_data = {}
    for symbol, price_history in data.items():
        print(f"graphing {len(price_history)} datapoints for {symbol}...")
        history_with_splits = []
        if symbol in splits.keys():
            for p in price_history:
                # check if date before split 
                if p[0] < splits[symbol][0]:
                    history_with_splits.append((p[0], p[1]/splits[symbol][1]))
                else:
                    history_with_splits.append((p[0], p[1]))
            clean_data[symbol] = dict(history_with_splits)
        else:
            clean_data[symbol] = dict(price_history)
    return clean_data