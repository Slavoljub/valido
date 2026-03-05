import sqlite3

conn = sqlite3.connect('data/sqlite/sample.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables in database:', tables)

# Check financial_transactions columns
print('\nfinancial_transactions columns:')
cursor.execute('PRAGMA table_info(financial_transactions)')
columns = cursor.fetchall()
for col in columns:
    print(f'  {col[1]} ({col[2]})')

conn.close()
