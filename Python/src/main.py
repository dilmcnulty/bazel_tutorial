import os
import requests
from flask import Flask, request, jsonify
from graph import build_chart
import google.auth.transport.requests
import google.oauth2.id_token

app = Flask(__name__)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8080")
allowed_symbols = ['AAPL', 'TSLA', 'VTI', 'AMZN']

def call_backend(url):
    if os.environ.get("K_SERVICE"):
        # Running in Cloud Run — need auth
        auth_req = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(auth_req, BACKEND_URL)
        headers = {"Authorization": f"Bearer {token}"}
        return requests.post(url, headers=headers)
    else:
        # Running locally — no auth needed
        return requests.post(url)

@app.route("/", methods=["GET"])
def index():
    return f"""
    <html><body>
        <h3>Available Symbols: {', '.join(allowed_symbols)}</h3>
        <form action="/chart" method="get">
            <input name="symbol" placeholder="Enter symbol" />
            <button type="submit">Show Chart</button>
        </form>
    </body></html>
    """

@app.route("/chart", methods=["GET"])
def chart():
    symbol = request.args.get("symbol", "").strip().upper()
    data = call_backend(f"{BACKEND_URL}?symbol={symbol}").json()
    if len(data) > 0:
        fig = build_chart(data)
        return fig.to_html()
    return "No data found for that symbol."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)