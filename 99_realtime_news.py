import sys
sys.path.append(".")
import time
import uvicorn
import asyncio
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect,websockets
from langchain_core.messages import HumanMessage,SystemMessage
from custom.workflows import realtime_news_flow_1
from mainbrainQA_core.core.state_base import MainGraphState
from mainbrainQA_core.common.utils import show_lg,show_er,show_wn,readConf

# des 还是从kafka中拿数据，只推送一条就结束。



app = FastAPI()
wbt_server_params = readConf("configs/websocket_server.conf")


@app.websocket("/new/realtime_news_ws")
async def main(websocket: WebSocket):
    await websocket.accept()
    state = MainGraphState()
    # state.user_input = [SystemMessage(content=""),HumanMessage(content="")]
    # state.parameters.update({"websocket_obj":websocket})
    # try:
    #     while True:
    #         try:
    #             state = await realtime_news_flow_1().ainvoke(state)
    #             await asyncio.sleep(0.1)
    #         except Exception as e:
    #             show_er(f"[maingraph]   {e}")
    #             time.sleep(2)
    #             continue
    # finally:
    #     # 清理任务
    #     await websocket.close()
    #     show_lg("Connection closed")
    # state = await realtime_news_flow_1().ainvoke(state)
    state = realtime_news_flow_1().invoke(state)
    # for s in  realtime_news_flow_1().stream(state):
    #     print(s)
    await asyncio.sleep(0.1)
    print(">outer>   ",state)
    # return state.tmp_value
    # try:
    #     state = await realtime_news_flow_1().ainvoke(state)
    #     await asyncio.sleep(0.1)
    # except Exception as e:
    #     show_er(f"[maingraph]   {e}")
    #     time.sleep(2)
    # finally:
    #     # 清理任务
    #     await websocket.close()
    #     show_lg("Connection closed")

if __name__ == "__main__":    
    uvicorn.run(app, host="120.241.223.8", port=8765)
