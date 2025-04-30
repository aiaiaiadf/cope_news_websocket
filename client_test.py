# from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# app = FastAPI()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             message = await websocket.receive_text()
#             print(f"Received message: {message}")
#             await websocket.send_text(">>> 收到")
#     except WebSocketDisconnect:
#         print("Client disconnected")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="localhost", port=8765)
# # uvicorn server_test:app --reload


# import asyncio
# import websockets
# n = 0
# async def echo(websocket): #, path):
#     global n
#     try:
#         async for message in websocket:
#             if message is not None:
#                 print(f"Received message: {n} - message")
#                 n+=1
#                 await websocket.send(">>> 收到")
#     except websockets.exceptions.ConnectionClosedError as e:
#         print(f"Connection closed with code={e.code}, reason={e.reason}")
#     await websocket.close(code=1000, reason="Normal closure")
# async def main():
#     # server = await websockets.serve(echo, "localhost", 8765)
#     server = await websockets.serve(echo, "120.241.223.8", 8765)
#     # server = await websockets.serve(echo, "0.0.0.0", 8765)
#     await server.wait_closed()

# if __name__ == "__main__":
#     asyncio.run(main())

#  python client_test.py

## bck
import asyncio
import websockets

async def listen():
    uri = "ws://120.241.223.8:8765/new/realtime_news_ws"
    async with websockets.connect(uri) as websocket:
        print("Connected to server")
        async for message in websocket:
            print(f"Received: {message}")

asyncio.run(listen())


# ## beathart
# import asyncio
# import websockets
# import json
# import time

# async def client():
#     uri = "ws://120.241.223.8:8765/new/realtime_news_ws"
#     async with websockets.connect(uri) as ws:
#         try:
#             while True:
#                 # 发送心跳
#                 # await ws.send(json.dumps({'type': 'heartbeat'}))
#                 # print("Sent heartbeat")
                
#                 # 接收服务端数据
#                 msg = await ws.recv()
#                 print(f"Received from server: {msg}")
                
#                 await asyncio.sleep(6)
                
#         except websockets.exceptions.ConnectionClosed:
#             print("Connection closed by server")

# asyncio.run(client())



# from fastapi import FastAPI, BackgroundTasks
# import asyncio
# import json
# from websockets import connect, WebSocketClientProtocol

# app = FastAPI()

# # 存储 WebSocket 连接状态
# client: WebSocketClientProtocol | None = None

# # 后台任务函数：负责连接和监听 WebSocket 服务器
# async def websocket_listener():
#     global client
#     url = "ws://120.241.223.8:8765/new/realtime_news_ws"
#     try:
#         # 建立连接
#         client = await connect(url)
#         print("[INFO] Connected to WebSocket server")
        
#         async for message in client:
#             # 确保消息是文本类型且可解析为 JSON
#             if isinstance(message, str):
#                 try:
#                     data = json.loads(message)  # 解析为字典
#                     print("[RECEIVED]", data)
#                 except json.JSONDecodeError:
#                     print("[ERROR] Invalid JSON format received")
#             else:
#                 print("[WARNING] Non-text message received")
                
#     except Exception as e:
#         print(f"[ERROR] Connection failed: {e}")
#     finally:
#         if client:
#             await client.close()
#             print("[INFO] Disconnected from WebSocket server")

# @app.on_event("startup")
# async def startup_event():
#     # 在应用启动时创建后台任务
#     loop = asyncio.get_running_loop()
#     loop.create_task(websocket_listener())

# @app.post("/send_message")
# async def send_message(message: dict, background_tasks: BackgroundTasks):
#     """发送消息到 WebSocket 服务器（如果已连接）"""
#     global client
#     if client and client.open:
#         msg_str = json.dumps(message)  # 将字典转为 JSON 字符串
#         await client.send(msg_str)
#         return {"status": "success"}
#     else:
#         return {"status": "error", "reason": "Not connected to server"}

