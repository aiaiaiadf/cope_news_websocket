import asyncio
import websockets
import json



class WebSocketServer:
    ...
    # def __init__(self, wst_params, config=None):

    #     """
    #     初始化WebSocket客户端
    #     :param uri: WebSocket服务器的URI
    #     :param config: 配置参数字典
    #     """
    #     self._parser(wst_params)
    #     self.uri = self.ip+":"+self.port
    #     self.config = config if config else {}
    #     self.websocket = connect(self.uri,ping_interval=self.ping_interval,ping_timeout=self.ping_timeout)

    # def _parser(self,wst_params):
    #     self.ip = wst_params['uri']
    #     self.port = wst_params['port']
    #     self.recondnect_delay = wst_params['recondnect_delay']
    #     self.send_interval = float(wst_params['send_interval'])
    #     self.ping_interval = int(wst_params['ping_interval'])
    #     self.ping_timeout = int(wst_params['ping_timeout'])
    
    # def process(self, data):
    #     self.websocket.send(json.dumps(data))
      
    # def release(self):
    #     self.websocket.close(code=1000, reason="Client initiated closure")
        # del self.websocket



# from websockets.sync.client import connect
# class WebSocketClient:
#     def __init__(self, wst_params, config=None):
#         """
#         初始化WebSocket客户端
#         :param uri: WebSocket服务器的URI
#         :param config: 配置参数字典
#         """
#         self._parser(wst_params)
#         self.uri = self.ip+":"+self.port
#         self.config = config if config else {}
#         self.websocket = connect(self.uri,ping_interval=self.ping_interval,ping_timeout=self.ping_timeout)

#     def _parser(self,wst_params):
#         self.ip = wst_params['uri']
#         self.port = wst_params['port']
#         self.recondnect_delay = wst_params['recondnect_delay']
#         self.send_interval = float(wst_params['send_interval'])
#         self.ping_interval = int(wst_params['ping_interval'])
#         self.ping_timeout = int(wst_params['ping_timeout'])
    
#     def process(self, data):
#         self.websocket.send(json.dumps(data))
      
#     def release(self):
#         self.websocket.close(code=1000, reason="Client initiated closure")
#         # del self.websocket




# class WebSocketClient:
#     def __init__(self, wst_params, config=None):
#         """
#         初始化WebSocket客户端
#         :param uri: WebSocket服务器的URI
#         :param config: 配置参数字典
#         """
#         self._parser(wst_params)
#         self.uri = self.ip+":"+self.port
#         self.config = config if config else {}
#     def _parser(self,wst_params):
#         self.ip = wst_params['uri']
#         self.port = wst_params['port']
#         self.out_time = wst_params['out_time']
    

#     def process(self, data):
#         with connect(self.uri) as websocket:
#             websocket.send(json.dumps(data))
#             # message = websocket.recv()
#             # print(f"Received: {message}")
#     def relaese(self):
#         del self.websocket




