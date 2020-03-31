# -*- coding:utf-8 -*-

import os
import time

from atp.config.default import get_config

config = get_config()
run_case_log_dir = config.RUN_CASE_LOG_DIR


def background_log_thread(room):
    """"""
    count = 0

    g = create_generator('{dir}run_{report_id}.log'.format(dir=run_case_log_dir, report_id=room))
    # g = create_generator('{dir}run_747.log'.format(dir=run_case_log_dir, report_id=room))
    from atp import socketio
    for i in g:
        socketio.sleep(0.1)

        if isinstance(i, list):
            for p in i:
                print(p)
                p = p.replace(' ', '&nbsp&nbsp')
                socketio.emit('server_response', {'time': p, 'count': count}, namespace='/test', room=room)
        else:
            i = i.replace(' ', '&nbsp&nbsp')
            count += 1
            socketio.emit('server_response', {'time': i, 'count': count}, namespace='/test', room=room)
            if '【END】测试结束' in i:
                break


def create_generator(file):
    # from atp import socketio
    s = 0
    while s < 10:
        is_exist = os.path.exists(file)
        if is_exist:
            break
        else:
            time.sleep(1)
            s += 1
    with open(file, 'r') as t:
        t.seek(0, 0)
        has_read = False
        _return_in_line = False

        while True:
            # 首次读取，直接返回已存在的所有行，类型是list
            if not has_read:
                exist_lines = t.readlines()
                has_read = True
                t.seek(0, 2)
                yield exist_lines

            # 按新增的行返回，类型是str
            elif _return_in_line:
                line = t.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line
            # 按新增的所有行返回，类型是list
            else:
                exist_lines = t.readlines()
                t.seek(0, 2)
                yield exist_lines


if __name__ == '__main__':
    pass
