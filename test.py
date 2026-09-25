from database import get_connection

conn = get_connection()

with conn.cursor() as cursor:
    cursor.execute("SELECT version()")
    print(cursor.fetchone())

conn.close()