import sqlite3

conn = sqlite3.connect('cafe_management.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS materials')

cursor.execute('''
CREATE TABLE materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    stock REAL NOT NULL
)
''')

conn.commit()
conn.close()

print("materials テーブルを再作成しました。")
