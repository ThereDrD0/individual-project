-- ============================================================================
-- Запросы для демонстрации работы с базой данных (Практическая работа № 7)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Тип 1 (SELECT / ORDER BY)
-- ----------------------------------------------------------------------------

-- 1.1 Список всех предметов с сортировкой по названию
SELECT
    id,
    name,
    description,
    owner_id
FROM items
ORDER BY name ASC;

-- 1.2 Список пользователей с сортировкой по возрасту (по убыванию) и имени
SELECT
    id,
    name,
    age,
    sex
FROM users
ORDER BY age DESC, name ASC;

-- ----------------------------------------------------------------------------
-- Тип 2 (WHERE)
-- ----------------------------------------------------------------------------

-- 2.1 Фильтрация свободных предметов (без текущего владельца)
SELECT
    id,
    name,
    description
FROM items
WHERE owner_id IS NULL;

-- 2.2 Фильтрация заявок в статусе ожидания рассмотрения
SELECT
    id,
    item_id,
    old_user_id,
    new_user_id,
    status,
    created_at
FROM requests
WHERE status = 'PENDING';

-- ----------------------------------------------------------------------------
-- Тип 3 (JOIN)
-- ----------------------------------------------------------------------------

-- 3.1 Каталог предметов с именами их текущих владельцев
SELECT
    i.id AS item_id,
    i.name AS item_name,
    i.description,
    u.id AS owner_id,
    u.name AS owner_name
FROM items AS i
LEFT JOIN users AS u ON i.owner_id = u.id
ORDER BY i.id ASC;

-- 3.2 Заявки со связанными предметами и именами участников
SELECT
    r.id AS request_id,
    i.name AS item_name,
    old_u.name AS from_user_name,
    new_u.name AS to_user_name,
    r.status,
    r.created_at
FROM requests AS r
JOIN items AS i ON r.item_id = i.id
JOIN users AS old_u ON r.old_user_id = old_u.id
JOIN users AS new_u ON r.new_user_id = new_u.id
ORDER BY r.created_at DESC;

-- ----------------------------------------------------------------------------
-- Тип 4 (COUNT / Агрегатные функции)
-- ----------------------------------------------------------------------------

-- 4.1 Подсчет общего числа предметов и количества свободных предметов
SELECT
    COUNT(*) AS total_items,
    COUNT(CASE WHEN owner_id IS NULL THEN 1 END) AS available_items,
    COUNT(owner_id) AS occupied_items
FROM items;

-- 4.2 Общее число передач и даты первой и последней передачи
SELECT
    COUNT(*) AS total_transfers,
    MIN(transferred_at) AS first_transfer_at,
    MAX(transferred_at) AS last_transfer_at
FROM transfers;

-- ----------------------------------------------------------------------------
-- Тип 5 (GROUP BY)
-- ----------------------------------------------------------------------------

-- 5.1 Количество предметов у каждого пользователя
SELECT
    u.id AS user_id,
    u.name AS user_name,
    COUNT(i.id) AS items_count
FROM users AS u
LEFT JOIN items AS i ON u.id = i.owner_id
GROUP BY u.id, u.name
ORDER BY items_count DESC, u.name ASC;

-- 5.2 Количество заявок по каждому предмету
SELECT
    i.id AS item_id,
    i.name AS item_name,
    COUNT(r.id) AS requests_count
FROM items AS i
LEFT JOIN requests AS r ON i.id = r.item_id
GROUP BY i.id, i.name
ORDER BY requests_count DESC, i.id ASC;

-- ----------------------------------------------------------------------------
-- Тип 6 (HAVING / Подзапросы)
-- ----------------------------------------------------------------------------

-- 6.1 Предметы, на которые подано более одной заявки
SELECT
    i.id AS item_id,
    i.name AS item_name,
    COUNT(r.id) AS requests_count
FROM items AS i
JOIN requests AS r ON i.id = r.item_id
GROUP BY i.id, i.name
HAVING COUNT(r.id) > 1;

-- 6.2 Свободные предметы без ожидающих (PENDING) заявок
SELECT
    id,
    name,
    description
FROM items
WHERE owner_id IS NULL
  AND id NOT IN (
      SELECT item_id
      FROM requests
      WHERE status = 'PENDING'
  )
ORDER BY id ASC;
