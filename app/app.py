import os
from contextlib import closing

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)


def query(sql):
    # Контекст соединения psycopg2 управляет транзакцией, closing закрывает его.
    with closing(psycopg2.connect(
        host=os.environ['DB_HOST'], dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
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
