import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Dya20231108@',
    database='test'
)

cur = conn.cursor()

# 获取所有表名
cur.execute('SHOW TABLES')
tables = cur.fetchall()

print('Table Name | Charset')
print('-' * 25)

# 对每个表检查字符集
for table in tables:
    table_name = table[0]
    try:
        cur.execute(f"SHOW CREATE TABLE {table_name}")
        result = cur.fetchone()
        create_statement = result[1]
        
        # 查找字符集信息
        if 'utf8mb4' in create_statement:
            charset = 'utf8mb4'
        elif 'latin1' in create_statement:
            charset = 'latin1'
        else:
            charset = 'unknown'
            
        print(f'{table_name} | {charset}')
    except Exception as e:
        print(f'{table_name} | Error: {str(e)}')

conn.close()