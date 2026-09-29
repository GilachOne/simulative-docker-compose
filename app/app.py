import os
from contextlib import closing

import psycopg2
from flask import Flask, jsonify

def get_env_var(name: str, default: str | None = None, is_required: bool = False) -> str | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        if is_required:
            raise RuntimeError(f"Переменная {name} должна быть установлена")
        return default
    return value


DB_HOST = get_env_var('DB_HOST', 'postgres')
try:
    DB_PORT = int(get_env_var('DB_PORT', '5432'))
    if not 1 <= DB_PORT <= 65535:
        raise ValueError
except ValueError:
    raise RuntimeError('Переменная DB_PORT должна быть целым числом от 1 до 65535') from None
DB_NAME = get_env_var('DB_NAME', is_required=True)
DB_USER = get_env_var('DB_USER', is_required=True)
DB_PASSWORD = get_env_var('DB_PASSWORD', is_required=True)

app = Flask(__name__)


def query(sql):
    # Контекст соединения psycopg2 управляет транзакцией, closing закрывает его.
    with closing(psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
        connect_timeout=5,
    )) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


@app.get('/health')
def health():
    query('SELECT 1')
    return jsonify(status='ok')


@app.get('/api/sales')
def sales():
    rows = query('SELECT id, sale_date, product, quantity, price '
                 'FROM sales ORDER BY sale_date, id')
    return jsonify([
        dict(id=row[0], date=row[1].isoformat(), product=row[2],
             quantity=row[3], price=str(row[4]), total=str(row[3] * row[4]))
        for row in rows
    ])


@app.get('/api/summary')
def summary():
    count, quantity, revenue = query(
        'SELECT count(*), coalesce(sum(quantity), 0), '
        'coalesce(sum(quantity * price), 0) FROM sales'
    )[0]
    return jsonify(sales=count, quantity=quantity, revenue=str(revenue))


@app.errorhandler(psycopg2.Error)
def database_error(error):
    app.logger.error('Database request failed: %s', type(error).__name__)
    return jsonify(error='База данных временно недоступна'), 503
