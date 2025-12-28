import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Dya20231108@',
    database='test'
)

cur = conn.cursor()
cur.execute('SHOW TABLE STATUS')
tables = cur.fetchall()

print('Table Name | Charset')
print('-' * 25)
for table in tables:
    print(f'{table[0]} | {table[13]}')

conn.close()