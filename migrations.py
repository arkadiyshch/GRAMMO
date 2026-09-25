import sqlite3
import psycopg2
from dotenv import load_dotenv
import os

# ============================================================
# НАСТРОЙКИ
# ============================================================



load_dotenv()

#Проверить, какая БД подгружается - тестовая или реальная
POSTGRES_DSN = os.getenv("DATABASE_URL")
SQLITE_DB = "data/GRAMMO.db"



# ============================================================
# ТАБЛИЦЫ И ПОРЯДОК МИГРАЦИИ
# ============================================================

TABLES = [
    "levels",
    "subscriptions",
    "difficulty",
    "users",
    "grammar_topics",
    "lexical_topics",
    "sentences",
    "payments",
    "user_answers",
    "user_difficulty",
    "user_levels",
    "user_subscriptions",
]


# ============================================================
# ПОДКЛЮЧЕНИЕ
# ============================================================

def connect_sqlite():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def connect_postgres():
    return psycopg2.connect(POSTGRES_DSN)


# ============================================================
# ПОЛУЧЕНИЕ ДАННЫХ ИЗ SQLITE
# ============================================================

def get_sqlite_rows(conn, table):
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table}")

    rows = cursor.fetchall()

    return rows


# ============================================================
# ПОЛУЧЕНИЕ НАЗВАНИЙ КОЛОНОК
# ============================================================

def get_sqlite_columns(conn, table):
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table})")

    columns = cursor.fetchall()

    return [column["name"] for column in columns]


# ============================================================
# МИГРАЦИЯ ОДНОЙ ТАБЛИЦЫ
# ============================================================
def migrate_table(sqlite_conn, postgres_conn, table):
    sqlite_rows = get_sqlite_rows(sqlite_conn, table)
    columns = get_sqlite_columns(sqlite_conn, table)

    if not sqlite_rows:
        print(f"{table}: 0 записей")
        return

    postgres_cursor = postgres_conn.cursor()

    column_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    query = f"""
        INSERT INTO {table} ({column_names})
        VALUES ({placeholders})
    """

    count = 0

    for sqlite_row in sqlite_rows:

        row = list(sqlite_row)

        # ----------------------------------------------------
        # subscriptions
        # ----------------------------------------------------

        if table == "subscriptions":

            # period_months: "NULL" -> 0
            period_months_index = columns.index("period_months")

            if row[period_months_index] == "NULL":
                row[period_months_index] = 0

            # daily_limit: "NULL" -> 0
            daily_limit_index = columns.index("daily_limit")

            if row[daily_limit_index] == "NULL":
                row[daily_limit_index] = 0

        postgres_cursor.execute(
            query,
            tuple(row)
        )

        count += 1

    print(f"{table}: {count} записей перенесено")


# ============================================================
# ОЧИСТКА POSTGRESQL
# ============================================================

def clear_postgres(postgres_conn):
    cursor = postgres_conn.cursor()

    tables = ", ".join(TABLES)

    query = f"""
        TRUNCATE TABLE {tables}
        RESTART IDENTITY
        CASCADE
    """

    cursor.execute(query)

    print("PostgreSQL очищена")


# ============================================================
# СБРОС SEQUENCE / IDENTITY
# ============================================================

def reset_sequences(postgres_conn):
    cursor = postgres_conn.cursor()

    print("\nСинхронизация ID...")

    for table in TABLES:

        query = f"""
            SELECT pg_get_serial_sequence(%s, 'id')
        """

        cursor.execute(query, (table,))

        result = cursor.fetchone()

        if not result:
            continue

        sequence_name = result[0]

        if not sequence_name:
            continue

        query = f"""
            SELECT MAX(id)
            FROM {table}
        """

        cursor.execute(query)

        max_id = cursor.fetchone()[0]

        if max_id is None:
            continue

        cursor.execute(
            "SELECT setval(%s, %s, true)",
            (sequence_name, max_id)
        )

        print(f"{table}: sequence -> {max_id}")


# ============================================================
# ПРОВЕРКА КОЛИЧЕСТВА ЗАПИСЕЙ
# ============================================================

def verify_migration(sqlite_conn, postgres_conn):
    print("\nПроверка количества записей:")

    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()

    success = True

    for table in TABLES:

        # SQLite
        sqlite_cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        sqlite_count = sqlite_cursor.fetchone()[0]

        # PostgreSQL
        postgres_cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        postgres_count = postgres_cursor.fetchone()[0]

        if sqlite_count == postgres_count:
            print(
                f"✓ {table}: "
                f"{sqlite_count} = {postgres_count}"
            )
        else:
            print(
                f"✗ {table}: "
                f"SQLite={sqlite_count}, "
                f"PostgreSQL={postgres_count}"
            )

            success = False

    return success


# ============================================================
# MAIN
# ============================================================

def main():

    print(f"SQLite: {SQLITE_DB}")
    print("Начинаем миграцию...\n")

    sqlite_conn = None
    postgres_conn = None

    try:

        # ----------------------------------------------------
        # Подключения
        # ----------------------------------------------------

        sqlite_conn = connect_sqlite()

        print("SQLite подключена")

        postgres_conn = connect_postgres()

        print("PostgreSQL подключена")

        # ----------------------------------------------------
        # Очистка PostgreSQL
        # ----------------------------------------------------

        print("\nОчищаем PostgreSQL...")

        clear_postgres(postgres_conn)

        # ----------------------------------------------------
        # Перенос таблиц
        # ----------------------------------------------------

        print()

        for table in TABLES:

            migrate_table(
                sqlite_conn,
                postgres_conn,
                table
            )

        # ----------------------------------------------------
        # Синхронизация ID
        # ----------------------------------------------------

        reset_sequences(postgres_conn)

        # ----------------------------------------------------
        # Проверка
        # ----------------------------------------------------

        print()

        success = verify_migration(
            sqlite_conn,
            postgres_conn
        )

        if not success:
            raise Exception(
                "Количество записей в SQLite и PostgreSQL не совпадает"
            )

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        postgres_conn.commit()

        print("\n================================")
        print("МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА")
        print("================================")

    except Exception as e:

        print("\nОШИБКА:")
        print(e)

        if postgres_conn:
            postgres_conn.rollback()
            print("PostgreSQL откатена")

    finally:

        if sqlite_conn:
            sqlite_conn.close()

        if postgres_conn:
            postgres_conn.close()


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    main()