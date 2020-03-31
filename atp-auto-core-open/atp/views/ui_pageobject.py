
from flask import Blueprint
from flask_restful import Resource
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.views.wrappers import developer_check

from atp.api.mysql_manager import UICasePageInfoManager, UICasePageObjectInfoManage

pageobject = Blueprint('pageobject_interface', __name__)


class PageObject(Resource):
    def __init__(self):
        self.upoim = UICasePageObjectInfoManage()
        self.data = get_request_json()

    def post(self, action):
        if action == 'add':
            return self.add_page_object(action)

        elif action == "edit":
            return self.add_page_object(action)

        elif action == "delete":
            return self.delete_page_object()

        elif action == 'queryByPageId':
            return self.query_by_pageId()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_page_object(self,action):
        if action == "add":
            try:
                page_object_name = self.data.pop("objectName")
                page_object_value = self.data.pop("objectValue")
                page_object_by = self.data.pop("objectBy")
                page_id = self.data.pop("pageId")
                simple_Desc = self.data.pop("simpleDesc", None)

            except KeyError:
                return make_response({"code": "100", "desc": "入参校验失败"})
            self.upoim.insert_ui_pageobject(object_name=page_object_name,
                                            simple_desc=simple_Desc,
                                            object_value=page_object_value,
                                            object_by=page_object_by,
                                            page_id=page_id)
            return make_response({"code": "000", "desc": "新增pageobject{}成功".format(page_object_name)})


        elif action == "edit":
            try:
                page_object_name = self.data.pop("objectName")
                page_object_value = self.data.pop("objectValue")
                page_object_by = self.data.pop("objectBy")
                object_id = self.data.pop("objectId")
                simple_Desc = self.data.pop("simpleDesc", None)

            except KeyError:
                return make_response({"code": "100", "desc": "入参校验失败"})
            self.upoim.eidt_page_object(object_name=page_object_name,
                                        simple_desc=simple_Desc,
                                        object_value=page_object_value,
                                        object_by=page_object_by,
                                        object_id=object_id)
            return make_response({"code": "000", "desc": "编辑pageobject{}成功".format(page_object_name)})

    def delete_page_object(self):
        try:
            page_object_name = self.data.pop("objectName")
            page_id = self.data.pop("pageId")

        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        self.upoim.delete_paget_object(object_name=page_object_name,

                                       page_id=page_id)
        return make_response({"code": "000", "desc": "删除pageobject{}成功".format(page_object_name)})

    @developer_check
    def query_by_pageId(self):
        try:
            page_id = self.data.pop("pageId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        response = []
        page_list = self.upoim.query_all_page_object(page_id=page_id)
        for page_obj in page_list:
            response.append({
                "id": page_obj.id,
                "object_name": page_obj.object_name,
                "object_by": page_obj.object_by,
                "object_value": page_obj.object_value,
                "simple_desc": page_obj.simple_desc,
                "page_id": page_id
            })
        return make_response({"code": "000", "desc": response})
