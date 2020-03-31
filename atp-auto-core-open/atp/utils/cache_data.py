# -*- coding:utf-8 -*-


class CacheData(object):
    def __init__(self):
        if not hasattr(self, "USERNAME_NICKNAME_DIC"):
            from atp.api.mysql_manager import UserManager
            self.USERNAME_NICKNAME_DIC = {row[0]: row[1] for row in UserManager.get_all_username_nickname()}

        if not hasattr(self, "TAG_BASE_MAP"):
            from atp.api.mysql_manager import TestcaseTagManager
            tag_objs = TestcaseTagManager.query_testcase_tag()
            self.TAG_BASE_MAP = {}
            for tag_obj in tag_objs:
                if tag_obj.tag_category not in self.TAG_BASE_MAP:
                    self.TAG_BASE_MAP[tag_obj.tag_category] = [{"tagId": tag_obj.id, "tagName": tag_obj.tag_name}]
                else:
                    self.TAG_BASE_MAP[tag_obj.tag_category].append({"tagId": tag_obj.id, "tagName": tag_obj.tag_name})

    def __new__(cls, *args, **kwargs):
        if not hasattr(CacheData, "_instance"):  # 反射
            CacheData._instance = object.__new__(cls)
        return CacheData._instance

    def get_username_nickname_dic(self):
        return self.USERNAME_NICKNAME_DIC

    def get_tag_base_map(self):
        return self.TAG_BASE_MAP
