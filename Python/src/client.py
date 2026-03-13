import requests
import json
from json import JSONDecodeError
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# class to retrieve data from eodhd, handle any errors, truncate data & return to main
class DataClient:
    data = dict[str, list[tuple[str,float]]]
    def __init__(self, data): 
        self.data = data

    # enter displayed symbol to remove it
    def add_or_remove(self, symbol: str) -> dict[str, list[tuple[str,float]]]: 
        if symbol in self.data.keys():
            print(f"removing {symbol}...")
            del self.data[symbol]
        else:
            self.get_data_for_symbol(symbol)
        return self.data
 
    # data fetching
    def get_data_for_symbol(self, symbol: str):
        url = f"https://eodhd.com/api/eod/{symbol}.US?api_token=demo&fmt=json"
        try:
            response = requests.get(url).json()
        except JSONDecodeError:
            print(f"error getting response for {symbol}")
            return 
        print(f"fetching {symbol}... got {response}")
        # only store last 5Y of data
        dataPoints = int(365 * (5/7) * 5) 
        sliced_response = response[-(dataPoints):]
        print(f"retrieved {len(sliced_response)}/{dataPoints} datapoints...")

        if isinstance(response, list):
            for e in sliced_response:
                if symbol not in self.data.keys():
                    self.data[symbol] = [(e['date'], e['close'])]
                else:
                    self.data[symbol].append((e['date'], e['close']))
            print(f"Added {symbol} successfully.")
        else:
            print(f"Could not find data for {symbol} (Check if 'demo' supports it).")

if __name__ == "__main__":
    client = DataClient({})

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            symbol = params.get('symbol', [''])[0].upper()
            if not symbol:
                self.send_response(400)
                self.end_headers()
                return
            data = client.add_or_remove(symbol)
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass  # suppress request logs

    print("Backend listening on port 8080...")
    HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
