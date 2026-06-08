## 5. Политика мягкого удаления (Soft Delete & Retention)
Для защиты пользовательских данных и реализации права на удаление аккаунта вводится механизм «периода охлаждения» сроком в 30 дней.
1. При запросе на удаление профиль помечается как неактивный (is_active = False), фиксируется дата запроса. Все активные JWT-сессии аннулируются. Данные физически не удаляются.
2. Если в течение 30 дней пользователь пытается войти повторно, ему предлагается восстановить профиль. При согласии аккаунт восстанавливается.
3. Автоматическая фоновая задача (Cron-job / Worker в Docker-окружении) раз в сутки физически удаляет из БД профили, у которых период охлаждения превысил 30 дней.

---

## 6. Структура сущностей в Базе Данных (PostgreSQL)

### Таблица users (Пользователи)
- id: UUID или Integer, Primary Key
- email: String, Unique, Nullable (если регистрация через бота)
- password_hash: String, Nullable (если регистрация через бота)
- telegram_id: BigInteger, Unique, Nullable (если регистрация через веб)
- role: String (по умолчанию "client", для админа "admin")
- is_active: Boolean (по умолчанию True)
- deletion_requested_at: DateTime, Nullable (дата запроса на удаление)
- birth_date: Date, Nullable (без значения по умолчанию)
- gender: String/Enum, Nullable (без значения по умолчанию)
- timezone: String, по умолчанию "Europe/Moscow"
- is_banned_from_commenting: Boolean (по умолчанию False)
- created_at: DateTime (UTC)
*Constraint:* CHECK (email IS NOT NULL OR telegram_id IS NOT NULL) (В базе не может быть записи без обоих идентификаторов связи).

### Таблица attacks (Приступы)
- id: UUID или Integer, Primary Key
- user_id: Foreign Key -> users.id (ON DELETE CASCADE)
- start_at: DateTime (строго в UTC, по умолчанию текущее время)
- duration_minutes: Integer, Nullable (если приступ еще продолжается)
- pain_intensity: Integer (шкала от 1 до 10)
- pain_characteristics: String/JSONB (характер боли: пульсирующая, давящая и др.)
- localization_zone: String (зона боли: висок слева, затылок и др.)
- created_at: DateTime (UTC)

### Таблица medication_intakes (Принятые лекарства)
- id: UUID или Integer, Primary Key
- attack_id: Foreign Key -> attacks.id (ON DELETE CASCADE)
- title: String (название препарата)
- dosage: String (дозировка, например "50 мг")
- taken_at: DateTime (UTC)

### Таблица articles (Статьи и новости)
- id: UUID или Integer, Primary Key
- title: String (заголовок)
- slug: String, Unique (для красивых URL)
- content: Text (содержимое статьи)
- is_published: Boolean (по умолчанию True)
- created_at: DateTime (UTC)
