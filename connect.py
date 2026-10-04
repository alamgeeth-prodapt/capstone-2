import sqlite3

conn = sqlite3.connect("telecom_ops.db")

cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tables = cursor.fetchall()

print(*tables)

cursor.execute("SELECT * FROM network_outages;")

towers = cursor.fetchall()


print(*towers)
conn.close()

