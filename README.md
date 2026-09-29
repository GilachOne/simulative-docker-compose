# Магазин: Docker Compose

Финальная практика: https://app.simulative.ru/course/34/1708

PostgreSQL хранит восемь учебных продаж, Python отдаёт JSON, Nginx показывает страницу и проксирует API.

## Запуск готовых образов

Нужны Docker Engine с Compose или Docker Desktop в режиме Linux-контейнеров. Python на хосте не нужен. Образы `1.1` опубликованы для `linux/amd64`.

Скопируйте весь шаблон настроек и при необходимости измените значения:

```sh
cp .env.example .env
```

В PowerShell:

```powershell
Copy-Item .env.example .env
```

Скачать и запустить — две отдельные команды:

```sh
docker compose --env-file .env pull
docker compose --env-file .env up -d --wait
```

Открыть http://localhost:8090 (или порт из `WEB_PORT`). В основном `docker-compose.yml` только `image`, без `build`: для запуска исходники приложения не нужны. Публичные образы можно скачать без входа в Docker Hub.

## Локальная сборка

Отдельный файл `compose.build.yaml` подключается явно. Он не участвует в обычном запуске.

```sh
docker compose --env-file .env -f docker-compose.yml -f compose.build.yaml build
docker compose --env-file .env up -d --pull never --wait
```

После этого контейнеры можно перезапускать без повторной сборки:

```sh
docker compose --env-file .env restart
```

Для публикации своих образов укажите свой `DOCKERHUB_USER` и новый `IMAGE_TAG` в `.env`, соберите их командой выше, затем:

```sh
docker login
docker compose --env-file .env -f docker-compose.yml -f compose.build.yaml push
```

## Настройки

`.env.example` содержит все параметры: `DOCKERHUB_USER`, `IMAGE_TAG`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `WEB_PORT`, `TZ`, `PGTZ`. Генератор `init_env.py` удалён: копирование шаблона не теряет переменные.

- В Compose есть значения по умолчанию, включая демонстрационный пароль `shop_password`. Можно запустить стенд и без `.env` командой `docker compose up -d --wait`.
- `POSTGRES_PORT` меняет порт PostgreSQL внутри сети и порт подключения Python. Порт БД на хост не публикуется. `POSTGRES_HOST` по умолчанию равен имени сервиса `postgres`.
- Общий YAML-блок задаёт всем сервисам `restart: unless-stopped`, сеть `shop`, таймзоны и ротацию логов `json-file` (50 МБ × 3 файла на контейнер). Отдельное слияние `environment` сохраняет таймзоны при добавлении переменных БД.
- Healthcheck PostgreSQL использует переменные самого контейнера: `$${POSTGRES_USER}`, `$${POSTGRES_DB}`, `$${PGPORT}`. Двойной доллар откладывает подстановку до запуска проверки внутри контейнера; значения поступают из `.env` через `environment`.
- При запуске Python отдельно от Compose задайте `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` в его окружении. Хост и порт имеют defaults `postgres` и `5432`; обязательные параметры проверяются при старте, ошибки называют переменную, но не раскрывают её значение.
- Изменение пользователя, БД или пароля в `.env` не переименовывает и не перенастраивает уже созданную БД в томе. Новые параметры инициализации проверяйте с новым Compose-проектом/пустым томом либо меняйте существующую БД средствами PostgreSQL.

## Устройство и проверка

- `postgres/` — PostgreSQL 16 и SQL начальных данных; SQL выполняется только на пустом томе.
- `app/` — Flask, psycopg2, Gunicorn; `/api/sales`, `/api/summary`, `/health`.
- `nginx/` — страница и reverse proxy.
- `pgdata` сохраняет БД; `nginx_logs` — каталог логов Nginx.
- БД и Python доступны внутри bridge-сети. HTTP опубликован только на localhost; удалённый стенд можно открыть через `ssh -L 8090:127.0.0.1:8090 USER@SERVER_IP`.
- Сервисы запускаются после успешного healthcheck зависимостей.

```sh
curl -f http://localhost:8090/health
curl -f http://localhost:8090/api/summary
docker compose --env-file .env ps
docker compose --env-file .env restart
curl -f http://localhost:8090/api/summary
```

В Windows используйте `curl.exe`. Ожидается 8 продаж, 27 единиц товара, выручка 8460.00 руб. После перезапуска данные сохраняются; HTTP проверяйте после возвращения сервисов в `healthy`.

`docker compose down` сохраняет тома. `down -v` удаляет данные и для обычной остановки не нужен.

## Docker Hub

Тег обновлённой работы: `1.1`.

- https://hub.docker.com/r/gilachone/simulative-docker-postgres
- https://hub.docker.com/r/gilachone/simulative-docker-python
- https://hub.docker.com/r/gilachone/simulative-docker-nginx

Результаты проверок находятся в `evidence/`; старые файлы без `review-` относятся к версии 1.0.

Подстановка переменных описана в [документации Docker Compose](https://docs.docker.com/reference/compose-file/interpolation/).
