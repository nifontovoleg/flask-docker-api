# Flask Docker API + Loki

[![EN](https://img.shields.io/badge/lang-English-blue?style=flat-square)](#-about)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Loki](https://img.shields.io/badge/Grafana-Loki-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)
[![LogQL](https://img.shields.io/badge/LogQL-sum_by(level)-purple?style=flat-square)](https://grafana.com/docs/loki/latest/query/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#-license)

**End-to-end learning lab:** Flask API → crypto log simulation → Loki push → Grafana (table + pie by level) → Docker Compose.

> Build → run → open `http://localhost:5000` → view logs in Grafana (`app="my_app"`).

---

## About

This project demonstrates a practical pipeline for a containerized Python backend with observability:

- Flask API with JSON endpoints
- Background crypto-event simulation (trades, orders, risk alerts)
- Log shipping to Loki via `POST /loki/api/v1/push`
- Grafana dashboard: recent logs table + pie chart by `level`
- Docker / Docker Compose

### Features

| Feature | Description |
|--------|-------------|
| **`/`** | Service greeting and status |
| **`/info`** | Hostname, platform, PID, UTC time |
| **`/calc/<a>/<b>`** | Sum, product, difference, quotient |
| **`send_log_to_loki`** | POST logs to Loki (`app="my_app"`) |
| **Crypto worker** | Random exchange events in a background thread |
| **Grafana dashboard** | Logs table + pie chart by level |
| **Dockerfile / Compose** | Runs on port `5000` |

---

## Tech stack

- **Python 3.12**
- **[Flask](https://flask.palletsprojects.com/)** — REST API
- **requests** — Loki push client
- **Grafana Loki** — log storage
- **Docker / Docker Compose** — packaging and run

---

## Project layout

```
flask-docker-api/
├── app.py                         # Flask API + crypto worker → Loki
├── main.py                        # Standalone crypto-exchange simulator → Loki
├── grafana/
│   └── dashboard-logs.json        # Dashboard: table + pie chart
├── Dockerfile
├── docker-compose.yml
├── requirements.txt               # flask, requests
└── README.md
```

---

## Quick start

### Option 1. Docker Compose (recommended)

```bash
git clone https://github.com/nifontovoleg/flask-docker-api.git
cd flask-docker-api

docker compose up --build -d
```

App URL: **http://localhost:5000**

```bash
docker compose down
```

### Option 2. Docker manually

```bash
docker build -t my-flask-app .
docker run -d -p 5000:5000 my-flask-app
```

### Option 3. Local run (no Docker)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open: http://localhost:5000

API smoke checks:

```bash
curl http://localhost:5000/
curl http://localhost:5000/info
curl http://localhost:5000/calc/10/2
```

---

## Logging to Loki

When you start `app.py`:

1. Flask listens on port `5000`
2. A background thread ships random crypto logs
3. Each API request also writes a log line

**`send_log_to_loki`** sends a `POST` to:

```text
http://<LOKI_HOST>:3100/loki/api/v1/push
```

Stream labels:

| Label | Default |
|-------|---------|
| `app` | `my_app` |
| `job` | `my_app` |
| `level` | `info` / `warn` / `error` |
| `service` | `my_app` |

Loki URL is set via the `LOKI_URL` constant in `app.py` / `main.py`.

### Standalone simulator

```bash
python main.py
```

Continuous exchange events (tickers, trades, orders, wallet, risk) with small delays.

Stdout only, no Loki:

```bash
python main.py --no-loki
```

---

## Grafana

Import the dashboard:

1. Grafana → **Dashboards** → **Import**
2. Select `grafana/dashboard-logs.json`
3. Folder: e.g. `Logging`
4. Datasource: **Loki** → **Import**

### Panels

1. **Recent logs table**

```logql
{app="$app"} |= `$search`
```

2. **Pie chart by level** (Sum + time range)

```logql
sum by (level) (count_over_time({app="$app"} |= `$search` [$__range]))
```

Dashboard variables:

- **App** — `label_values(app)` (select `my_app`)
- **String Match** — text filter
- **Time range** — `$__range` (Last 5/15 minutes, etc.)

If the dashboard shows **No data**:

1. Run `python app.py` (console should print `[OK]`)
2. In Grafana select **App = my_app**
3. Set time range to **Last 15 minutes** and refresh

Explore check:

```logql
{app="my_app"}
```

---

## API

### `GET /`

```json
{
  "message": "Hello from crypto-backend!",
  "status": "ok"
}
```

### `GET /info`

```json
{
  "hostname": "ec8cf5230606",
  "platform": "...",
  "pid": 1234,
  "service": "crypto-backend",
  "time": "2026-07-22 17:00:00 UTC"
}
```

### `GET /calc/<a>/<b>`

Example: `http://localhost:5000/calc/10/2`

```json
{
  "a": 10,
  "b": 2,
  "sum": 12,
  "product": 20,
  "difference": 8,
  "quotient": 5.0
}
```

> On division by zero, `quotient` is `null`.

---

## Useful commands

```bash
# Rebuild after code changes
docker compose up --build -d

# Container logs
docker compose logs -f

# List containers
docker ps
```

---

## Troubleshooting

### Port `5000` is busy

```bash
docker compose down
```

### Changes in `app.py` are not visible in Docker

```bash
docker compose up --build -d
```

`docker restart` alone does **not** pick up new code.

### Grafana is empty for App = my_app

- The app must be running and printing `[OK]`
- Loki URL must be reachable from the host running `app.py`
- Select App = `my_app`, not older labels like `crypto-backend` / `test-app`

---

## Why this project

| Goal | Outcome |
|------|---------|
| Docker / Compose | Build and run a Python service in a container |
| Flask API | Simple JSON endpoints |
| Observability | Push logs to Loki with `app` / `level` labels |
| Grafana | Logs table and pie chart powered by LogQL |

---

## License

MIT — free to use for personal and learning projects.

---

<p align="center">
  Built with ☕ for learning Docker, backend APIs, and Loki<br>
  <a href="https://github.com/nifontovoleg">@nifontovoleg</a> · <a href="https://www.nifontovv.ru/">nifontovv.ru</a>
</p>
