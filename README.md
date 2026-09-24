# Магазин: Docker Compose

Финальная практика модуля Docker: https://app.simulative.ru/course/34/1708

Небольшой отчет о продажах. PostgreSQL хранит данные, Python читает их и отдает JSON, Nginx показывает страницу и передает запросы API в Python.

## Запуск

Нужны Docker Engine с Compose и Python 3 для создания локального `.env`.

```sh
python3 init_env.py
docker compose up -d --build --wait
```

Открыть http://localhost:8090. На удаленной машине можно использовать SSH-туннель: `ssh -L 8090:127.0.0.1:8090 root@SERVER_IP`, затем открыть тот же адрес на своем компьютере.

## Устройство

- `postgres/` — PostgreSQL 16 и восемь учебных продаж. Данные создаются только при первом запуске с пустым томом.
- `app/` — Flask, psycopg2 и Gunicorn. Маршруты `/api/sales`, `/api/summary`, `/health`.
- `nginx/` — статическая страница и reverse proxy.
- `pgdata` сохраняет БД, `nginx_logs` — логи веб-сервера.
- Сервисы соединены собственной bridge-сетью `shop`. БД и Python не публикуют порты хоста. Веб-порт доступен на localhost.
- Запуск идет после успешных healthcheck зависимостей. Пароль берется из `.env`; он не включен в код, архив и Docker-образы.

## Проверка

```sh
curl -f http://localhost:8090/health
curl -f http://localhost:8090/api/summary
docker compose ps
docker compose restart
```

Ожидаемый результат: 8 продаж, 27 единиц товара, выручка 8460.00 руб. После перезапуска данные сохраняются.

`docker compose down` останавливает стенд и сохраняет данные. Опция `-v` удаляет тома и данные, для обычной остановки она не нужна.

## Образы Docker Hub

Опубликованные образы (тег `1.0`):

- https://hub.docker.com/r/gilachone/simulative-docker-postgres
- https://hub.docker.com/r/gilachone/simulative-docker-python
- https://hub.docker.com/r/gilachone/simulative-docker-nginx

Для запуска готовых образов добавьте `DOCKERHUB_USER=gilachone` в созданный `.env` и выполните `docker compose up -d --no-build --pull always --wait`.

Укажите `DOCKERHUB_USER` в `.env`, войдите через `docker login`, затем:

```sh
docker compose build
docker compose push
```

На другой машине после создания `.env` с тем же `DOCKERHUB_USER`: `docker compose up -d --no-build --pull always --wait`.

Результаты запуска и проверки сохранения данных лежат в `evidence/`.
