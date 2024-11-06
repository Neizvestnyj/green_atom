import sqlite3


def clear_all_tables(db_path):
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Для каждой таблицы создаем запрос на удаление всех данных
    for table in tables:
        table_name = table[0]
        # Пропускаем системные таблицы
        if table_name not in ('sqlite_sequence',):
            cursor.execute(f"DELETE FROM {table_name};")
            print(f"Очистили таблицу: {table_name}")

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


# Пример использования
clear_all_tables('organization_service/organisation_service.db')
clear_all_tables('storage_service/storage_service.db')
