# Настройка базы данных

## Структура базы данных

База данных содержит следующие таблицы:

1. `telegram_users` - информация о пользователях Telegram
   - id (BIGINT) - ID пользователя в Telegram
   - first_name (text) - имя пользователя
   - username (text) - username пользователя
   - last_name (text) - фамилия пользователя
   - language_code (text) - код языка
   - is_premium (bool) - премиум статус
   - is_admin (bool) - статус администратора

2. `coworking` - статус коворкинг-пространства
   - id (serial) - уникальный идентификатор
   - status (text) - текущий статус
   - responsible_id (BIGINT) - ID ответственного
   - duration (integer) - длительность
   - created_at (timestamp) - время создания

3. `profiles` - профили пользователей
   - user_id (BIGINT) - ID пользователя
   - fio (text) - ФИО
   - email (text) - email
   - educational_group (text) - учебная группа
   - portfolio_link (text) - ссылка на портфолио
   - majors (text[]) - направления
   - external_links (text[]) - внешние ссылки
   - skills (text[]) - навыки
   - mentor (boolean) - статус ментора
   - company (text) - компания

4. `subscriptions` - подписки пользователей
   - id (BIGINT) - ID пользователя
   - coworking (boolean) - подписка на коворкинг
   - hack_club (boolean) - подписка на клуб хакинга
   - design_club (boolean) - подписка на дизайн-клуб
   - gamedev_club (boolean) - подписка на клуб геймдева
   - ai_club (boolean) - подписка на AI клуб
   - robot_club (boolean) - подписка на клуб робототехники
   - itam_digest (boolean) - подписка на дайджест

5. `clubs` - информация о клубах
   - id (serial) - уникальный идентификатор
   - name (text) - название клуба
   - description (text) - описание
   - chat_link (text) - ссылка на чат
   - created_at (timestamp) - время создания

6. `admin_invite_codes` - коды приглашения администраторов
   - id (serial) - уникальный идентификатор
   - code (text) - код приглашения
   - rights_ids (BIGINT[]) - ID прав
   - admin_id (BIGINT) - ID создателя
   - user_id (BIGINT) - ID пользователя
   - created_at (timestamp) - время создания
   - activated_at (timestamp) - время активации

7. `admin_rights` - права администраторов
   - id (serial) - уникальный идентификатор
   - name (text) - название права

8. `admin_rights_users` - связь пользователей и прав
   - id (serial) - уникальный идентификатор
   - user_id (BIGINT) - ID пользователя
   - right_id (BIGINT) - ID права

9. `clubs_additional_links` - дополнительные ссылки клубов
   - id (serial) - уникальный идентификатор
   - club_id (BIGINT) - ID клуба
   - link (text) - ссылка
   - button_name (text) - название кнопки
   - created_at (timestamp) - время создания

## Поднятие базы данных

### Локально

1. Установите PostgreSQL 15
2. Создайте базу данных:
   ```bash
   createdb your_db_name
   ```
3. Примените скрипт создания таблиц:
   ```bash
   psql -d your_db_name -f postgres/create_tables.sql
   ```

## Проверка подключения

Для проверки подключения к базе данных можно использовать:

```bash
psql -h localhost -U your_user -d your_db_name
```

## Миграции

При изменении структуры базы данных:
1. Измените файл `create_tables.sql`
2. Примените изменения:
   ```bash
   psql -d your_db_name -f postgres/create_tables.sql
   ```

## Резервное копирование

Для создания резервной копии базы данных:

```bash
pg_dump -h localhost -U your_user -d your_db_name > backup.sql
```

Для восстановления из резервной копии:

```bash
psql -h localhost -U your_user -d your_db_name < backup.sql
``` 
