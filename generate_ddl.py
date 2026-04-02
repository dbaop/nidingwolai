#!/usr/bin/env python3
# 生成数据库DDL脚本

from datetime import datetime
from app import create_app, db
from app.models import User, Activity, Enrollment, Review, InterestTag, ActivityTag

app = create_app()

with app.app_context():
    # 生成DDL脚本
    from sqlalchemy.schema import CreateTable
    
    # 获取所有表
    tables = []
    for model in [User, Activity, Enrollment, Review, InterestTag, ActivityTag]:
        tables.append(model.__table__)
    
    # 生成创建表的SQL语句
    ddl_script = """
-- 数据库初始化脚本
-- 生成时间: {}

-- 禁用外键约束检查
SET FOREIGN_KEY_CHECKS = 0;

-- 删除现有表
DROP TABLE IF EXISTS activity_tag;
DROP TABLE IF EXISTS interest_tag;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS activity;
DROP TABLE IF EXISTS user;

-- 启用外键约束检查
SET FOREIGN_KEY_CHECKS = 1;

""".format(datetime.utcnow())
    
    # 添加创建表的语句
    for table in tables:
        ddl_script += str(CreateTable(table)) + '\n\n'
    
    # 保存到文件
    with open('db_schema.sql', 'w', encoding='utf-8') as f:
        f.write(ddl_script)
    
    print('✅ 数据库DDL脚本生成完成')
    print('文件保存为: db_schema.sql')
