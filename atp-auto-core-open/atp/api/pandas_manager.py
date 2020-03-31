# -*- coding:utf-8 -*-

import pandas as pd
from numpy import NaN
from atp.utils.tools import json_dumps


class PandasManager(object):

    def __int__(self):
        self.excel_path = None

    def base_testcase_excel_to_data(self, excel_path, column_list=None):
        if not column_list:
            column_list = []
        xl = pd.ExcelFile(excel_path)

        data_list = []

        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)

            sheet_data = []

            for i in df.index.values:
                try:
                    row_data = df.ix[i, column_list].fillna('').to_dict()
                except KeyError:
                    row_data = None
                if row_data:
                    sheet_data.append(row_data)

            data_list.append({sheet_name: sheet_data})

        return data_list


if __name__ == '__main__':
    example_excel = r'业务用例.xls'
    pdm = PandasManager()
    data = pdm.base_testcase_excel_to_data(example_excel, ['模块', '用例标题', '前置条件', '操作步骤', '预期结果', '备注'])
    print(data)
