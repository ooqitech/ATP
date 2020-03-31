
from flask import  Blueprint
from  flask_restful import  Resource
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.mysql_manager import  UICasePageInfoManager,UICasePageObjectInfoManage
page = Blueprint('page_interface', __name__)


class Page(Resource):
    def __init__(self):
        self.upim = UICasePageInfoManager()
        self.data = get_request_json()

    def post(self,action):
        if action == 'add':
            return self.add_page()
        if action == 'pageList':
            return  self.pagelist_by_systemid()

    def add_page(self):
        try:
            page_name = self.data.pop("pageName")
            system_id = self.data.pop("systemId")
            simple_Desc = self.data.pop("simpleDesc", None)

        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        self.upim.insert_ui_page(page_name=page_name,simple_desc=simple_Desc,system_id=system_id )
        return make_response({"code": "000", "desc": "新增page{}成功".format(page_name)})

    def pagelist_by_systemid(self):
        try:
            system_id = self.data.pop("systemId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        objs = self.upim.query_ui_pages(system_id=system_id)
        page_list = []
        for obj in objs:
            page_dict={
                "id":obj.id,
                "pageName":obj.page_name
            }
            page_list.append(page_dict)
        return make_response({"code": "000", "desc": page_list})
