import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Dya20231108@',
    database='test'
)

cur = conn.cursor()

# 需要更新字符集的表列表
tables_to_update = [
    'alembic_version',
    'feedbacks',
    'interest_tag',
    'orders',
    'service',
    'service_items',
    'therapist_services',
    'therapists',
    'user_addresses',
    'user_tag',
    'users'
]

print('Updating tables to utf8mb4 charset...')
for table_name in tables_to_update:
    try:
        sql = f"ALTER TABLE {table_name} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        cur.execute(sql)
        print(f'Successfully updated {table_name}')
    except Exception as e:
        print(f'Error updating {table_name}: {str(e)}')

conn.commit()
conn.close()
print('All tables updated!')