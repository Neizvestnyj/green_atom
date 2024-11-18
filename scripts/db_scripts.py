import sqlite3
from typing import List, Tuple


def clear_all_tables(db_path: str) -> None:
    """
    Очищает все таблицы в базе данных, удаляя из них все записи.

    :param db_path: Путь к SQLite базе данных
    :raises sqlite3.Error: Если возникает ошибка при подключении или выполнении запроса
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables: List[Tuple[str]] = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            if table_name not in ('sqlite_sequence',):
                cursor.execute(f"DELETE FROM {table_name};")
                print(f"Очистили таблицу: {table_name}")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при очистке таблиц: {e}")
        raise
    finally:
        conn.close()


def drop_all_tables(db_path: str) -> None:
    """
    Удаляет все таблицы из базы данных.

    :param db_path: Путь к SQLite базе данных
    :raises sqlite3.Error: Если возникает ошибка при подключении или выполнении запроса
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables: List[Tuple[str]] = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            if table_name not in ('sqlite_sequence',):
                cursor.execute(f"DROP TABLE {table_name};")
                print(f"Удалили таблицу: {table_name}")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении таблиц: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        print("Очистка таблиц в organisation_service.db")
        clear_all_tables('../organisation_service/organisation_service.db')

        print("\nОчистка таблиц в storage_service.db")
        clear_all_tables('../storage_service/storage_service.db')
    except Exception as e:
        print(f"Ошибка выполнения: {e}")
