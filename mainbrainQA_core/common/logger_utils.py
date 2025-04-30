# import os
# import logging
# from logging.handlers import TimedRotatingFileHandler




# class Logger():
#     def __init__(self,name:str="log_",level:str="debug",out_dir:str="logs"):
#         self.log = logging.getLogger()
#         self.name = name
#         self.level = level
#         self.out_dir = out_dir
#         mkdir(self.out_dir)
#         self._set_level()
#         self._init_content()

#     def _set_level(self):
#         if "debug" == self.level.lower():
#             level = logging.DEBUG
#         elif "error" == self.level.lower():
#             level = logging.ERROR
#         elif "warning" == self.level.lower():
#             level = logging.WARNING
#         else:
#             level = logging.INFO
#         self.log.setLevel(level)

#     def _init_content(self):
#         handler = TimedRotatingFileHandler(
#             filename=os.path.join(self.out_dir,self.name),       # 日志文件名前缀+日期格式
#             when='midnight',                   # 在午夜滚动
#             interval=1,                        # 每隔1天切换
#             backupCount=30,                     # 保留最近7天的日志文件
#             encoding='utf-8'                   # 支持中文编码
#         )
#         formatter = logging.Formatter(
#             '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',  # 时间 | 级别 | 消息
#             datefmt='%Y-%m-%d'                 # 时间格式
#         )
#         handler.setFormatter(formatter)
