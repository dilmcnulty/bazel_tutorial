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
        auth_req = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(auth_req, BACKEND_URL)
        headers = {"Authorization": f"Bearer {token}"}
        return requests.post(url, headers=headers)
    else:
        return requests.post(url)

@app.route("/", methods=["GET"])
def index():
    symbols_html = "".join(
        f'<div class="symbol-row" id="avail-{sym}">'
        f'<span class="symbol-name">{sym}</span>'
        f'<button class="add-btn" onclick="toggleSymbol(\'{sym}\')">+</button>'
        f'</div>'
        for sym in allowed_symbols
    )

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Stock Chart</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; display: flex; height: 100vh; overflow: hidden; background: #f8f9fa; }}

        .sidebar {{ width: 180px; padding: 20px 12px; border-right: 1px solid #dee2e6; background: white; overflow-y: auto; flex-shrink: 0; }}
        .sidebar h3 {{ font-size: 11px; font-weight: 600; color: #868e96; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }}
        .symbol-row {{ display: flex; align-items: center; justify-content: space-between; padding: 8px 6px; border-radius: 6px; transition: background 0.1s; }}
        .symbol-row:hover {{ background: #f1f3f5; }}
        .symbol-name {{ font-weight: 600; font-size: 14px; color: #212529; }}
        .add-btn {{
            background: #28a745; color: white; border: none; border-radius: 50%;
            width: 26px; height: 26px; cursor: pointer; font-size: 18px; line-height: 1;
            display: flex; align-items: center; justify-content: center;
            transition: background 0.15s, transform 0.1s;
            flex-shrink: 0;
        }}
        .add-btn:hover {{ background: #218838; transform: scale(1.1); }}
        .add-btn.active {{ background: #6c757d; font-size: 14px; }}
        .add-btn:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}

        .main {{ flex: 1; display: flex; flex-direction: column; padding: 20px; overflow: hidden; min-width: 0; }}

        .active-bar {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; min-height: 38px; margin-bottom: 14px; }}
        .active-bar-label {{ font-size: 11px; font-weight: 600; color: #868e96; text-transform: uppercase; letter-spacing: 1px; margin-right: 4px; }}
        .active-tag {{
            display: flex; align-items: center; gap: 5px;
            background: #e7f5ff; border: 1px solid #74c0fc; border-radius: 20px;
            padding: 4px 10px 4px 12px; font-size: 13px; font-weight: 700; color: #1971c2;
            animation: fadein 0.2s ease;
        }}
        @keyframes fadein {{ from {{ opacity: 0; transform: scale(0.85); }} to {{ opacity: 1; transform: scale(1); }} }}
        .remove-btn {{
            background: none; border: none; color: #fa5252; cursor: pointer;
            font-size: 17px; font-weight: 700; line-height: 1; padding: 0;
            display: flex; align-items: center; transition: color 0.1s;
        }}
        .remove-btn:hover {{ color: #c92a2a; }}
        .remove-btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}

        .chart-area {{ flex: 1; position: relative; background: white; border-radius: 10px; border: 1px solid #dee2e6; overflow: hidden; }}
        #chart-container {{ width: 100%; height: 100%; }}
        #chart-container > div:not(.empty-state) {{ width: 100% !important; height: 100% !important; }}
        #loading {{
            display: none; position: absolute; inset: 0;
            flex-direction: column; align-items: center; justify-content: center;
            background: white; z-index: 10;
        }}
        #loading.visible {{ display: flex; }}
        .spinner {{
            width: 42px; height: 42px; border: 3px solid #dee2e6;
            border-top-color: #339af0; border-radius: 50%;
            animation: spin 0.8s linear infinite; margin-bottom: 14px;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        #loading p {{ color: #868e96; font-size: 14px; }}

        .empty-state {{
            position: absolute; inset: 0; display: flex; flex-direction: column;
            align-items: center; justify-content: center; color: #adb5bd;
        }}
        .empty-state .icon {{ font-size: 48px; margin-bottom: 12px; }}
        .empty-state p {{ font-size: 15px; }}

        #error-toast {{
            display: none; position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
            background: #fa5252; color: white; padding: 12px 20px; border-radius: 8px;
            font-size: 14px; font-weight: 500; z-index: 100; max-width: 480px; text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        #error-toast.visible {{ display: block; animation: fadein 0.2s ease; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>Symbols</h3>
        {symbols_html}
    </div>
    <div class="main">
        <div class="active-bar" id="active-bar">
            <span class="active-bar-label">Active</span>
            <span id="no-active" style="color:#adb5bd;font-size:13px;">None selected</span>
        </div>
        <div class="chart-area">
            <div id="loading"><div class="spinner"></div><p>Fetching data&hellip;</p></div>
            <div id="error-toast"></div>
            <div id="chart-container">
                <div class="empty-state">
                    <div class="icon">📈</div>
                    <p>Select a symbol to get started</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let active = [];
        let busy = false;

        async function toggleSymbol(symbol) {{
            if (busy) return;
            busy = true;
            setLoading(true);
            setAllButtons(true);

            try {{
                const resp = await fetch('/toggle?symbol=' + encodeURIComponent(symbol), {{ method: 'POST' }});
                const data = await resp.json();
                if (!resp.ok || data.error) {{
                    showError(data.error || 'Something went wrong. Please try again.');
                }} else {{
                    active = data.active_symbols;
                    renderActiveTags();
                    renderChart(data.chart_html);
                    syncSidebarButtons();
                }}
            }} catch (e) {{
                console.error('Error toggling symbol:', e);
                showError('Could not reach the server. Is the backend running?');
            }} finally {{
                setLoading(false);
                setAllButtons(false);
                busy = false;
            }}
        }}

        function setLoading(show) {{
            document.getElementById('loading').classList.toggle('visible', show);
        }}

        function setAllButtons(disabled) {{
            document.querySelectorAll('.add-btn, .remove-btn').forEach(b => b.disabled = disabled);
        }}

        function renderActiveTags() {{
            const bar = document.getElementById('active-bar');
            const noActive = document.getElementById('no-active');
            // Remove old tags
            bar.querySelectorAll('.active-tag').forEach(t => t.remove());
            if (active.length === 0) {{
                noActive.style.display = '';
            }} else {{
                noActive.style.display = 'none';
                active.forEach(sym => {{
                    const tag = document.createElement('div');
                    tag.className = 'active-tag';
                    tag.id = 'tag-' + sym;
                    tag.innerHTML = `${{sym}}<button class="remove-btn" onclick="toggleSymbol('${{sym}}')" title="Remove ${{sym}}">&#x2715;</button>`;
                    bar.appendChild(tag);
                }});
            }}
        }}

        function renderChart(html) {{
            const container = document.getElementById('chart-container');
            if (!html) {{
                container.innerHTML = '<div class="empty-state"><div class="icon">📈</div><p>Select a symbol to get started</p></div>';
                return;
            }}
            container.innerHTML = html;
            // Re-execute injected scripts (needed for Plotly)
            container.querySelectorAll('script').forEach(old => {{
                const s = document.createElement('script');
                s.textContent = old.textContent;
                old.replaceWith(s);
            }});
        }}

        let errorTimer = null;
        function showError(msg) {{
            const toast = document.getElementById('error-toast');
            toast.textContent = msg;
            toast.classList.add('visible');
            clearTimeout(errorTimer);
            errorTimer = setTimeout(() => toast.classList.remove('visible'), 5000);
        }}

        function syncSidebarButtons() {{
            document.querySelectorAll('.add-btn').forEach(btn => {{
                btn.classList.remove('active');
                btn.textContent = '+';
                btn.title = '';
            }});
            active.forEach(sym => {{
                const btn = document.querySelector('#avail-' + sym + ' .add-btn');
                if (btn) {{
                    btn.classList.add('active');
                    btn.textContent = '✓';
                    btn.title = sym + ' is active';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

@app.route("/toggle", methods=["POST"])
def toggle():
    symbol = request.args.get("symbol", "").strip().upper()
    if not symbol or symbol not in allowed_symbols:
        return jsonify({"error": "Invalid symbol"}), 400

    try:
        resp = call_backend(f"{BACKEND_URL}?symbol={symbol}")
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Backend error for {symbol}: {e}")
        return jsonify({"error": f"Failed to fetch data for {symbol}. The backend may be unavailable."}), 502

    if not isinstance(data, dict):
        return jsonify({"error": f"Unexpected response from backend for {symbol}."}), 502

    active_symbols = list(data.keys())

    if data:
        try:
            fig = build_chart(data)
            chart_html = fig.to_html(full_html=False, include_plotlyjs=False)
        except Exception as e:
            print(f"Chart build error: {e}")
            return jsonify({"error": "Failed to render chart."}), 500
    else:
        chart_html = ""

    return jsonify({"active_symbols": active_symbols, "chart_html": chart_html})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)
