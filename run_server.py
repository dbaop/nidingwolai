#!/usr/bin/env python3
# 运行服务器脚本

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)