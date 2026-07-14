# 🐳 Flask Docker API

**Простой Flask REST API** в Docker — учебный проект по контейнеризации бэкенда: три эндпоинта, `Dockerfile` и запуск через Docker Compose на порту `5000`.

> Собрал → запустил → открыл `http://localhost:5000` — готово.

---

## 📌 О проекте

Проект показывает минимальный, но рабочий пайплайн для Python-бэкенда:

- Flask-приложение с JSON-эндпоинтами
- сборка Docker-образа одной командой
- запуск контейнера вручную или через `docker compose`
- воспроизводимое окружение без локальной установки Flask

Подходит как учебный пример для изучения **Docker** и **Docker Compose** на практике.

### Возможности

| Функция | Описание |
|--------|----------|
| 🏠 **`/`** | Приветствие и статус сервиса |
| ℹ️ **`/info`** | Hostname контейнера и текущее UTC-время |
| 🧮 **`/calc/<a>/<b>`** | Сумма, произведение, разность и частное двух чисел |
| 🐳 **Dockerfile** | Образ на базе `python:3.12-slim` |
| 🧩 **Compose** | Один сервис `web` на порту `5000` |

---

## 🛠 Технологии

- **Python 3.12**
- **[Flask](https://flask.palletsprojects.com/)** — лёгкий REST API
- **Docker** — сборка и запуск образа
- **Docker Compose** — оркестрация одной командой

---

## 📁 Структура проекта

```
flask-docker-api/
├── app.py              # Flask API: /, /info, /calc
├── Dockerfile          # Образ приложения
├── docker-compose.yml  # Запуск сервиса на порту 5000
├── requirements.txt    # Зависимости Python
└── README.md           # Документация
```

---

## 🚀 Быстрый старт

### Вариант 1. Docker Compose (рекомендуется)

```bash
git clone https://github.com/nifontovoleg/flask-docker-api.git
cd flask-docker-api

docker compose up -d
```

Приложение будет доступно по адресу: **http://localhost:5000**

Остановка:

```bash
docker compose down
```

### Вариант 2. Docker вручную

```bash
docker build -t my-flask-app .
docker run -d -p 5000:5000 my-flask-app
```

Проверка:

```bash
curl http://localhost:5000/
curl http://localhost:5000/info
curl http://localhost:5000/calc/10/2
```

---

## 🔌 API

### `GET /`

```json
{
  "message": "Hello from Flask!",
  "status": "ok"
}
```

### `GET /info`

```json
{
  "hostname": "ec8cf5230606",
  "service": "my-flask-app",
  "time": "2026-07-14 13:31:34 UTC"
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

> При делении на ноль поле `quotient` вернёт `null`.

---

## 🧪 Локальный запуск без Docker

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

---

## ⚙️ Полезные команды

```bash
# Пересборка после изменений в коде
docker compose up --build -d

# Логи контейнера
docker compose logs -f

# Список контейнеров
docker ps
```

---

## ⚠️ Решение проблем

### Порт `5000` занят

Остановите старый контейнер или другой процесс на порту:

```bash
docker compose down
```

### Изменения в `app.py` не видны

Нужно пересобрать образ:

```bash
docker compose up --build -d
```

`docker restart` сам по себе **не** подхватывает новый код.

---

## 🎯 Зачем этот проект

| Цель | Результат |
|------|-----------|
| Изучить Docker | Сборка и запуск Python-сервиса в контейнере |
| Изучить Compose | Поднятие стека одной командой |
| Практика Flask | Простые JSON-эндпоинты без лишней сложности |

---

## 📄 Лицензия

MIT — используйте свободно в личных и учебных проектах.

---

<p align="center">
  Сделано с ☕ для изучения Docker и бэкенда<br>
  <a href="https://github.com/nifontovoleg">@nifontovoleg</a> · <a href="https://www.nifontovv.ru/">nifontovv.ru</a>
</p>
