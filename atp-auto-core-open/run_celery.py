# -*- coding:utf-8 -*-

from atp.app import create_app
from atp.extensions import celery

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        celery.start()
