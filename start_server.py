#!/usr/bin/env python3
# 稳定的服务器启动脚本

from app import create_app
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log',
    filemode='w'
)

# 控制台日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger = logging.getLogger(__name__)
logger.addHandler(console_handler)

def main():
    logger.info('正在创建应用实例...')
    app = create_app()
    
    logger.info('打印所有注册的路由:')
    for rule in app.url_map.iter_rules():
        if 'api/enrollments' in str(rule):
            logger.info(f'  {rule} -> {rule.endpoint}')
    
    # 使用不同的端口
    port = 5001
    logger.info(f'尝试在端口 {port} 上启动服务器...')
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f'启动服务器失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()