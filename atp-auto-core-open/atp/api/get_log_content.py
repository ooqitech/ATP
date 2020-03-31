
class GetLogContent(object):
    """
    获取服务器日志文件内容
    """
    def __init__(self, logs, start_with, end_with):
        self.logs = logs
        self.start_with = start_with
        self.end_with = end_with

    def get_log_content(self):
        """
        解析日志内容，根据起始标签，找到符合要求的内容列表，然后根据搜索关键字找到符合条件的内容
        :return:
        """
        if self.start_with and self.end_with:
            filtered_logs = self.logs.split(self.start_with)[1].split(self.end_with)[0]
        elif self.start_with:
            filtered_logs = self.logs.split(self.start_with)[1]
        elif self.end_with:
            filtered_logs = self.logs.split(self.end_with)[0]
        else:
            filtered_logs = self.logs

        return filtered_logs


if __name__ == '__main__':
    pass
