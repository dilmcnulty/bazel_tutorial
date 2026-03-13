# Stock Viewer
A full-stack stock data visualization tool demonstrating a containerized microservice architecture built entirely with Bazel. Once executed, the user can type a stock from an available list (due to EODHD's free api-tier limitations) to fetch the last 5 years of data from the server and display that in a graph. The user can then type the same symbol to remove it from the chart, or additional symbols to overlay and compare their history on the chart.

The application is split into a decoupled backend service and an interactive frontend. The backend fetches historical equity data from a live market API (eodhd), maintains in-memory state, and exposes it over HTTP. The frontend is an interactive CLI that queries the backend and renders interactive Plotly charts with range selectors and a timeline slider.

This build decouples the frontend and backend to prevent build compatibility issues with C extensions like NumPy for pandas. An image is created from client.py and then started with docker

### Running Application on Mac
There are 3 commands required to build and run the application on Mac.

1. `bazel run //Python:tarball --platforms=//Python:linux_arm64 --noincompatible_enable_cc_toolchain_resolution`
2. `docker run -p 8080:8080 trading-backend:latest`
3. `bazel run //Python:viewer`

The backend server starts on port 8080, and the frontend POSTs to http://localhost:8080?symbol=AAPL whenever you enter a symbol. The response JSON (the current data dict) is passed straight to build_chart().

### Technical Details
* Bazel monorepo: all targets (py_binary, py_library, py_test) are defined in a single BUILD file with explicit, hermetic dependency graphs via rules_python and a pinned pip lockfile
* Containerized backend: the backend service is packaged into a reproducible Docker image using Bazel's rules_oci and rules_pkg, with cross-compilation support for both linux/amd64 and linux/arm64. No Dockerfile required
* Stock split correction: historical prices are automatically adjusted for known stock splits (e.g., TSLA 3:1, AMZN 20:1) before charting, ensuring accurate long-term comparisons
* Tested: unit tests validate the split-adjustment logic across pre-split, post-split, and unaffected symbols
* Frontend/backend separation: the frontend communicates with the backend over HTTP, allowing the backend to be deployed and scaled independently