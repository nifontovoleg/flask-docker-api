# 🐳 Flask Docker API + Loki

**Flask REST API** в Docker с эмуляцией крипто-бэкенда и отправкой логов в **Grafana Loki**.  
Учебный проект: контейнеризация, observability, LogQL и дашборд Grafana.

> Собрал → запустил → открыл `http://localhost:5000` → смотри логи в Grafana.

---

## 📌 О проекте

Проект показывает рабочий пайплайн:

- Flask API с JSON-эндпоинтами
- фоновая эмуляция крипто-событий (сделки, ордера, risk-алерты)
- отправка логов в Loki через `POST /loki/api/v1/push`
- дашборд Grafana: таблица логов + круговая диаграмма по `level`
- Docker / Docker Compose

### Возможности

| Функция | Описание |
|--------|----------|
| 🏠 **`/`** | Приветствие и статус сервиса |
| ℹ️ **`/info`** | Hostname, platform, PID, UTC-время |
| 🧮 **`/calc/<a>/<b>`** | Сумма, произведение, разность и частное |
| 📡 **`send_log_to_loki`** | POST логов в Loki (`app="my_app"`) |
| 🪙 **Crypto worker** | Случайные события биржи в фоне |
| 📊 **Grafana dashboard** | Таблица логов + pie по level |
| 🐳 **Dockerfile / Compose** | Запуск на порту `5000` |

---

## 🛠 Технологии

- **Python 3.12**
- **[Flask](https://flask.palletsprojects.com/)** — REST API
- **requests** — push в Loki
- **Grafana Loki** — хранение логов
- **Docker / Docker Compose** — контейнеризация

---

## 📁 Структура проекта

```
flask-docker-api/
├── app.py                         # Flask API + crypto worker → Loki
├── main.py                        # Отдельный эмулятор крипто-биржи → Loki
├── grafana/
│   └── dashboard-logs.json        # Дашборд: таблица + pie chart
├── Dockerfile
├── docker-compose.yml
├── requirements.txt               # flask, requests
└── README.md
```

---

## 🚀 Быстрый старт

### Вариант 1. Docker Compose (рекомендуется)

```bash
git clone https://github.com/nifontovoleg/flask-docker-api.git
cd flask-docker-api

docker compose up --build -d
```

Приложение: **http://localhost:5000**

```bash
docker compose down
```

### Вариант 2. Docker вручную

```bash
docker build -t my-flask-app .
docker run -d -p 5000:5000 my-flask-app
```

### Вариант 3. Локально без Docker

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Откройте: http://localhost:5000

Проверка API:

```bash
curl http://localhost:5000/
curl http://localhost:5000/info
curl http://localhost:5000/calc/10/2
```

---

## 📡 Логи в Loki

При запуске `app.py`:

1. поднимается Flask на порту `5000`
2. фоновый поток шлёт случайные крипто-логи
3. каждый запрос к API тоже пишет лог

Функция **`send_log_to_loki`** делает `POST` на:

```text
http://<LOKI_HOST>:3100/loki/api/v1/push
```

Метки потока:

| Label | Значение по умолчанию |
|-------|------------------------|
| `app` | `my_app` |
| `job` | `my_app` |
| `level` | `info` / `warn` / `error` |
| `service` | `my_app` |

URL Loki задаётся в `app.py` / `main.py` константой `LOKI_URL`.

### Отдельный эмулятор

```bash
python main.py
```

Непрерывный поток событий биржи (тикеры, сделки, ордера, wallet, risk) с задержками.  
Только консоль, без Loki:

```bash
python main.py --no-loki
```

---

## 📊 Grafana

Импорт дашборда:

1. Grafana → **Dashboards** → **Import**
2. файл `grafana/dashboard-logs.json`
3. Folder: например `Logging`
4. Datasource: **Loki** → **Import**

### Панели

1. **Таблица последних логов**

```logql
{app="$app"} |= `$search`
```

2. **Круговая диаграмма по level** (Sum + time range)

```logql
sum by (level) (count_over_time({app="$app"} |= `$search` [$__range]))
```

Переменные дашборда:

- **App** — `label_values(app)` (выбери `my_app`)
- **String Match** — текстовый фильтр
- **Time range** — `$__range` (Last 5/15 minutes и т.д.)

Если в дашборде **No data**:

1. запусти `python app.py` (в консоли должны быть `[OK]`)
2. в Grafana выбери **App = my_app**
3. поставь time range **Last 15 minutes** и обнови страницу

Проверка в Explore:

```logql
{app="my_app"}
```

---

## 🔌 API

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

Пример: `http://localhost:5000/calc/10/2`

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

> При делении на ноль `quotient` = `null`.

---

## ⚙️ Полезные команды

```bash
# Пересборка после изменений
docker compose up --build -d

# Логи контейнера
docker compose logs -f

# Список контейнеров
docker ps
```

---

## ⚠️ Решение проблем

### Порт `5000` занят

```bash
docker compose down
```

### Изменения в `app.py` не видны в Docker

```bash
docker compose up --build -d
```

`docker restart` **не** подхватывает новый код.

### Grafana пустая при App = my_app

- приложение должно быть запущено и печатать `[OK]`
- Loki URL должен быть доступен с машины, где крутится `app.py`
- выбери App = `my_app`, не `crypto-backend` / `test-app` (это старые метки)

---

## 🎯 Зачем этот проект

| Цель | Результат |
|------|-----------|
| Docker / Compose | Сборка и запуск Python-сервиса в контейнере |
| Flask API | Простые JSON-эндпоинты |
| Observability | Push логов в Loki, метки `app` / `level` |
| Grafana | Таблица логов и pie chart на LogQL |

---

## 📄 Лицензия

MIT — используйте свободно в личных и учебных проектах.

---

<p align="center">
  Сделано с ☕ для изучения Docker, бэкенда и Loki<br>
  <a href="https://github.com/nifontovoleg">@nifontovoleg</a> · <a href="https://www.nifontovv.ru/">nifontovv.ru</a>
</p>
