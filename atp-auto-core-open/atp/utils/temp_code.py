# -*- coding:utf-8 -*-


from atp.api.mysql_manager import ApiTestcaseReuseRecordManager


def test_insert():
    ApiTestcaseReuseRecordManager.insert_record(api_testcase_id=1, total_times=10)


if __name__ == '__main__':

    pass

