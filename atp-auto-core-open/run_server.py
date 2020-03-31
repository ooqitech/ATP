# -*- coding:utf-8 -*-

# from atp import app
# from atp import socketio
from atp.app import create_app
app = create_app()

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=7000, debug=True)
    # socketio.run(app, host='0.0.0.0', port=7000, debug=True)
    app.run(host='0.0.0.0', port=7000, debug=True)


"""

# 启动Flask服务命令
python3 run_server.py

"""
