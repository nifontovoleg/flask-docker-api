"""Flask-приложение: API + эмуляция крипто-бэкенда с отправкой логов в Loki."""

from __future__ import annotations

import os
import platform
import random
import socket
import threading
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify

LOKI_URL = "http://31.31.201.103:3100/loki/api/v1/push"
app = Flask(__name__)

PAIRS = ("BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "TON/USDT")
LEVELS = ("info", "info", "info", "warn", "error")
EVENTS = (
    "price_tick",
    "trade_executed",
    "order_update",
    "wallet_op",
    "http_request",
    "risk_alert",
)


def send_log_to_loki(
    message: str,
    job: str = "my_app",
    level: str = "info",
    app_name: str = "my_app",
) -> None:
    """POST сообщений в Loki: /loki/api/v1/push."""
    timestamp = str(int(time.time() * 1_000_000_000))
    payload = {
        "streams": [
            {
                "stream": {
                    "app": app_name,
                    "job": job,
                    "level": level,
                    "service": "my_app",
                },
                "values": [[timestamp, message]],
            }
        ]
    }
    try:
        response = requests.post(LOKI_URL, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"[OK] [{level}] {message}", flush=True)
        else:
            print(f"[ERR] send failed: {response.status_code}", flush=True)
    except Exception as e:
        print(f"[ERR] {e}", flush=True)


def build_crypto_message() -> tuple[str, str]:
    level = random.choice(LEVELS)
    event = random.choice(EVENTS)
    pair = random.choice(PAIRS)
    price = round(random.uniform(0.1, 100_000), 4)
    qty = round(random.uniform(0.001, 5.0), 6)
    user = f"u_{random.randint(10000, 99999)}"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    msg = (
        f'ts={ts} event="{event}" pair={pair} price={price} '
        f"qty={qty} user={user} status={'ok' if level != 'error' else 'fail'} "
        f'msg="crypto backend {event}"'
    )
    return msg, level


def crypto_worker(interval: float = 0.5) -> None:
    """Фоновый поток: постоянно шлёт случайные крипто-логи в Loki."""
    while True:
        message, level = build_crypto_message()
        send_log_to_loki(message, level=level)
        time.sleep(interval + random.uniform(-0.2, 0.3))


@app.get("/")
def index():
    send_log_to_loki("GET /", level="info")
    return {"message": "Hello from crypto-backend!", "status": "ok"}


@app.get("/info")
def info():
    send_log_to_loki("GET /info", level="info")
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "pid": os.getpid(),
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "service": "crypto-backend",
    }


@app.get("/calc/<int:a>/<int:b>")
def calc(a: int, b: int):
    send_log_to_loki(f"GET /calc/{a}/{b}", level="info")
    return jsonify(
        {
            "a": a,
            "b": b,
            "sum": a + b,
            "product": a * b,
            "difference": a - b,
            "quotient": a / b if b != 0 else None,
        }
    )


if __name__ == "__main__":
    worker = threading.Thread(target=crypto_worker, daemon=True)
    worker.start()
    app.run(host="0.0.0.0", port=5000)
