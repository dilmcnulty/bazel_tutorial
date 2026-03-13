import requests
from graph import build_chart

BACKEND_URL = "http://localhost:8080"
allowed_symbols = ['AAPL', 'TSLA', 'VTI', 'AMZN']

while True:
    print(f"Available Symbols: {allowed_symbols}")
    symbol = input('Enter a US symbol to display or remove from the currently displayed list, or \'quit\': ').strip().upper()

    if symbol == 'QUIT':
        break

    data = requests.post(f"{BACKEND_URL}?symbol={symbol}").json()
    if len(data) > 0:
        chart = build_chart(data)
        chart.show()


