"""Простое Flask-приложение для работы в Docker."""

import socket
from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return {
        "message": "Hello from Flask!",
        "status": "ok",
    }


@app.get("/info")
def info():
    return {
        "hostname": socket.gethostname(),
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "service": "my-flask-app",
    }


@app.get("/calc/<int:a>/<int:b>")
def calc(a, b):
    return jsonify({
        "a": a,
        "b": b,
        "sum": a + b,
        "product": a * b,
        "difference": a - b,
        "quotient": a / b if b != 0 else None,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
