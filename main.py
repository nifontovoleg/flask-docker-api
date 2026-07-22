#!/usr/bin/env python3
"""Эмулятор бэкенда крипто-биржи: случайные события + push логов в Loki."""

from __future__ import annotations

import argparse
import random
import sys
import time
from datetime import datetime, timezone
from typing import Any

import requests

LOKI_URL = "http://31.31.201.103:3100/loki/api/v1/push"
DEFAULT_URL = LOKI_URL

PAIRS = (
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "TON/USDT",
    "AVAX/USDT",
)

BASE_PRICES: dict[str, float] = {
    "BTC/USDT": 97_500.0,
    "ETH/USDT": 3_420.0,
    "SOL/USDT": 178.0,
    "BNB/USDT": 645.0,
    "XRP/USDT": 2.35,
    "DOGE/USDT": 0.18,
    "TON/USDT": 5.6,
    "AVAX/USDT": 38.0,
}

SIDES = ("buy", "sell")
ORDER_TYPES = ("limit", "market", "stop-limit")
STATUSES = ("open", "filled", "partially_filled", "cancelled")
NETWORKS = ("ethereum", "bsc", "tron", "solana", "ton")
LEVELS = ("info", "info", "info", "info", "warn", "error")


def send_log_to_loki(
    message: str,
    job: str = "crypto-backend",
    level: str = "info",
    url: str = LOKI_URL,
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
                    "service": "crypto-backend",
                },
                "values": [[timestamp, message]],
            }
        ]
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"[OK] [{level}] {message}", flush=True)
        else:
            print(f"[ERR] send failed: {response.status_code}", flush=True)
    except Exception as e:
        print(f"[ERR] {e}", flush=True)


def ts_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def jitter_price(pair: str) -> float:
    base = BASE_PRICES[pair]
    # ±0.8% шум вокруг базовой цены
    return round(base * (1.0 + random.uniform(-0.008, 0.008)), 8)


def rand_user() -> str:
    return f"u_{random.randint(10000, 99999)}"


def rand_order_id() -> str:
    return f"ord_{random.randint(10**8, 10**9 - 1)}"


def rand_txid() -> str:
    return "0x" + "".join(random.choices("0123456789abcdef", k=16))


def event_price_tick() -> dict[str, Any]:
    pair = random.choice(PAIRS)
    price = jitter_price(pair)
    change = round(random.uniform(-2.5, 2.5), 3)
    return {
        "event": "price_tick",
        "level": "info",
        "pair": pair,
        "price": price,
        "change_24h_pct": change,
        "volume_24h": round(random.uniform(1e5, 5e8), 2),
        "msg": f"ticker update {pair}={price}",
    }


def event_trade() -> dict[str, Any]:
    pair = random.choice(PAIRS)
    price = jitter_price(pair)
    qty = round(random.uniform(0.001, 12.0), 6)
    side = random.choice(SIDES)
    return {
        "event": "trade_executed",
        "level": "info",
        "pair": pair,
        "side": side,
        "price": price,
        "qty": qty,
        "notional_usdt": round(price * qty, 2),
        "order_id": rand_order_id(),
        "user_id": rand_user(),
        "fee_usdt": round(price * qty * random.uniform(0.0005, 0.002), 4),
        "msg": f"{side} {qty} {pair} @ {price}",
    }


def event_order() -> dict[str, Any]:
    pair = random.choice(PAIRS)
    price = jitter_price(pair)
    status = random.choice(STATUSES)
    level = "warn" if status == "cancelled" else "info"
    return {
        "event": "order_update",
        "level": level,
        "pair": pair,
        "side": random.choice(SIDES),
        "type": random.choice(ORDER_TYPES),
        "status": status,
        "price": price,
        "qty": round(random.uniform(0.01, 50.0), 6),
        "order_id": rand_order_id(),
        "user_id": rand_user(),
        "msg": f"order {status} on {pair}",
    }


def event_orderbook() -> dict[str, Any]:
    pair = random.choice(PAIRS)
    mid = jitter_price(pair)
    spread = mid * random.uniform(0.0001, 0.0015)
    return {
        "event": "orderbook_snapshot",
        "level": "info",
        "pair": pair,
        "best_bid": round(mid - spread / 2, 8),
        "best_ask": round(mid + spread / 2, 8),
        "bid_depth": round(random.uniform(5.0, 800.0), 4),
        "ask_depth": round(random.uniform(5.0, 800.0), 4),
        "msg": f"orderbook refresh {pair}",
    }


def event_wallet() -> dict[str, Any]:
    asset = random.choice(("BTC", "ETH", "USDT", "SOL", "TON"))
    action = random.choice(("deposit", "withdraw", "transfer_internal"))
    amount = round(random.uniform(0.01, 25_000.0), 6)
    ok = random.random() > 0.12
    level = "info" if ok else "error"
    return {
        "event": "wallet_op",
        "level": level,
        "action": action,
        "asset": asset,
        "amount": amount,
        "network": random.choice(NETWORKS),
        "txid": rand_txid() if action != "transfer_internal" else None,
        "user_id": rand_user(),
        "status": "ok" if ok else "fail",
        "msg": (
            f"{action} {amount} {asset} completed"
            if ok
            else f"{action} {amount} {asset} failed: insufficient balance / network error"
        ),
    }


def event_api() -> dict[str, Any]:
    routes = (
        "GET /api/v1/ticker",
        "GET /api/v1/orderbook",
        "POST /api/v1/orders",
        "DELETE /api/v1/orders",
        "GET /api/v1/balances",
        "POST /api/v1/withdraw",
        "GET /api/v1/trades",
        "WS /stream/prices",
    )
    route = random.choice(routes)
    latency_ms = round(random.uniform(3.0, 420.0), 1)
    status = random.choices(
        (200, 200, 200, 201, 400, 429, 500), weights=(55, 20, 10, 5, 5, 3, 2)
    )[0]
    if status >= 500:
        level = "error"
    elif status >= 400:
        level = "warn"
    else:
        level = "info"
    return {
        "event": "http_request",
        "level": level,
        "route": route,
        "status_code": status,
        "latency_ms": latency_ms,
        "user_id": rand_user() if random.random() > 0.3 else "anonymous",
        "msg": f"{route} -> {status} in {latency_ms}ms",
    }


def event_risk() -> dict[str, Any]:
    pair = random.choice(PAIRS)
    flags = (
        "large_order_detected",
        "velocity_check",
        "wash_trade_suspect",
        "withdrawal_limit_near",
        "price_deviation",
    )
    flag = random.choice(flags)
    score = round(random.uniform(0.1, 0.99), 3)
    level = "error" if score > 0.85 else "warn"
    return {
        "event": "risk_alert",
        "level": level,
        "pair": pair,
        "flag": flag,
        "risk_score": score,
        "user_id": rand_user(),
        "msg": f"risk:{flag} score={score} pair={pair}",
    }


EVENT_BUILDERS = (
    event_price_tick,
    event_price_tick,
    event_trade,
    event_trade,
    event_order,
    event_orderbook,
    event_wallet,
    event_api,
    event_api,
    event_risk,
)


def format_line(job: str, payload: dict[str, Any], seq: int) -> str:
    level = payload["level"]
    parts = [
        f"ts={ts_iso()}",
        f"level={level}",
        f"job={job}",
        f"seq={seq}",
        f'event="{payload["event"]}"',
        f'msg="{payload["msg"]}"',
    ]
    skip = {"event", "level", "msg"}
    for key, value in payload.items():
        if key in skip or value is None:
            continue
        parts.append(f"{key}={value}")
    return " ".join(parts)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Эмулятор крипто-биржи: непрерывный поток случайных событий → Loki",
    )
    p.add_argument("--url", default=DEFAULT_URL, help="Loki push URL")
    p.add_argument("--job", default="crypto-backend", help="label job")
    p.add_argument(
        "-i",
        "--interval",
        type=float,
        default=0.4,
        help="базовая пауза между событиями (сек)",
    )
    p.add_argument(
        "--jitter",
        type=float,
        default=0.35,
        help="случайный разброс паузы ±jitter (сек)",
    )
    p.add_argument(
        "--no-loki",
        action="store_true",
        help="только печатать в stdout, без отправки в Loki",
    )
    return p.parse_args()


def sleep_with_jitter(base: float, jitter: float) -> None:
    delay = max(0.05, base + random.uniform(-jitter, jitter))
    time.sleep(delay)


def main() -> int:
    args = parse_args()
    seq = 0
    print(
        f"crypto-exchange simulator started job={args.job} "
        f"loki={'off' if args.no_loki else args.url}",
        flush=True,
    )
    try:
        while True:
            payload = random.choice(EVENT_BUILDERS)()
            seq += 1
            line = format_line(args.job, payload, seq)
            level = payload["level"]

            if not args.no_loki:
                send_log_to_loki(line, job=args.job, level=level, url=args.url)
            else:
                print(f"[{seq}] {level}: {line}", flush=True)

            sleep_with_jitter(args.interval, args.jitter)
    except KeyboardInterrupt:
        print(f"\nstopped, events={seq}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
