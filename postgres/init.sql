CREATE TABLE sales (
    id integer PRIMARY KEY,
    sale_date date NOT NULL,
    product text NOT NULL,
    quantity integer NOT NULL CHECK (quantity > 0),
    price numeric(10,2) NOT NULL CHECK (price >= 0)
);

-- Учебные данные. Скрипт выполняется при первом создании тома БД.
INSERT INTO sales VALUES
    (1, '2026-09-01', 'Кофе', 3, 450),
    (2, '2026-09-01', 'Чай', 5, 220),
    (3, '2026-09-02', 'Кофе', 2, 450),
    (4, '2026-09-02', 'Какао', 4, 310),
    (5, '2026-09-03', 'Чай', 6, 220),
    (6, '2026-09-03', 'Какао', 1, 310),
    (7, '2026-09-04', 'Кофе', 4, 450),
    (8, '2026-09-04', 'Чай', 2, 220);
