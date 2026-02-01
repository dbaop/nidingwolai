#!/usr/bin/env python3
# 稳定的服务器启动脚本

import sys
import os
from app import create_app

def main():
    print('=== 启动稳定服务器 ===')
    print(f'Python版本: {sys.version}')
    print(f'当前目录: {os.getcwd()}')
    
    try:
        # 创建应用实例
        app = create_app()
        print('应用创建成功')
        
        # 打印路由信息
        print('\n=== API路由信息 ===')
        for rule in app.url_map.iter_rules():
            if 'api/' in str(rule):
                print(f'  {rule}')
        
        # 启动服务器
        port = 5002
        print(f'\n=== 启动服务器在端口 {port} ===')
        print('服务器启动中...')
        print('按 Ctrl+C 停止服务器')
        
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        print(f'启动失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()