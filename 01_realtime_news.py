import sys
sys.path.append(".")
import time
import uvicorn
import asyncio
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect,websockets
from custom.workflows import realtime_news_flow_4
from mainbrainQA_core.common.llm_utils import str2dict
from mainbrainQA_core.core.state_base import MainGraphState
from custom.prompt.prompt_vector import classify_msg,classify_prompt
from mainbrainQA_core.common.utils import show_lg,show_er,show_wn,readConf
from mainbrainQA_core.common.kafka_utils import KFKConsumer
from typing import Set

app = FastAPI()



connected_clients: Set[WebSocket] = set()

async def broadcast(message: str):
    for conn in list(connected_clients):
        try:
            await conn.send_json(message)
        except Exception:
            connected_clients.discard(conn)



@app.websocket("/new/realtime_news_ws")
async def main(websocket: WebSocket):
    # 参数
    kafka_params = readConf("configs/kafka.conf")
    # 其他
    await websocket.accept()
    connected_clients.add(websocket)
    state = MainGraphState()
    classify_prompt.set_system_msg(classify_msg)
    try:
        kfk_client = KFKConsumer(kafka_params)
        kfk_client.partition = 0
        kfk_client.set_bias()
        # ~~~~~~~~~~~~~~~~
        messages = next(kfk_client.consumer)
        if not messages:
                assert BufferError,"not get data from kafka"
                print("未收到任何消息")
        data = messages.value.decode()
        #^^^^^  N
        # bs = int(kafka_params["bs"])
        # messages = kfk_client.consumer.poll(timeout_ms=1000, max_records=bs)
        #     for i,topic, msgs in enumerate(messages.items()):
        #         if msgs:
        #             message = next(iter(msgs))
        #             print(f"Received message: {message.value}")
        #         if i == bs-1:
        #             break
        # # ~~~~~~~~~~~~~~~~
        try:
            data_dct = str2dict(data.replace("'",'"'))
        except:
            data_dct = str2dict(data)
        check_data = f"{data_dct['title']} , {data_dct['content']}"


        classify_prompt.set_human_msg(check_data)
        msg = classify_prompt.get_messages()
        state.user_input = msg
        state.parameters.update({"data_dct":data_dct})
        state = realtime_news_flow_4().invoke(state)

        await broadcast(state["tmp_value"])
        # websocket.send_json(state["tmp_value"])
        await asyncio.sleep(0.1)
    except Exception as e:
        show_er(f"[maingraph]   {e}")
        time.sleep(2)
    finally:
        # 清理任务
        connected_clients.discard(websocket)
        show_lg("Connection closed")







# @app.websocket("/new/realtime_news_ws")
# async def main(websocket: WebSocket):
#     # 参数
#     kafka_params = readConf("configs/kafka.conf")
    
#     await websocket.accept()

#     state = MainGraphState()

#     classify_prompt.set_system_msg(classify_msg)
    
#     kfk_client = KFKConsumer(kafka_params)
#     # offsets =  kfk_client.partition
    
#     # ~~~~~~~~~~~~~~~~
#     messages = next(kfk_client.consumer)
#     if not messages:
#             assert BufferError,"not get data from kafka"
#             print("未收到任何消息")
#     data = messages.value.decode()
#     #^^^^^
#     # bs = int(kafka_params["bs"])
#     # # ~~~~~~~~~~~~~~~~
#     try:
#         data_dct = str2dict(data.replace("'",'"'))
#     except:
#         data_dct = str2dict(data)
#     check_data = f"{data_dct['title']} , {data_dct['content']}"

#     # print(data,type(data))
#     # print(data_dct,type(data_dct))

    
#     classify_prompt.set_human_msg(check_data)
#     msg = classify_prompt.get_messages()
#     state.user_input = msg
#     state.parameters.update({"data_dct":data_dct})
#     state = realtime_news_flow_4().invoke(state)
#     # print("123123123123 >>>>>    ",state,type(state))
#     # print(">>>>M<MM    ",state["tmp_value"])
    
#     websocket.send_json(state["tmp_value"])
#     await asyncio.sleep(0.1)
#     # print(">outer>   ",state)





#     # state.parameters.update({"websocket_obj":websocket})
#     # try:
#     #     while True:
#     #         try:
#     #             state = await realtime_news_flow_1().ainvoke(state)
#     #             await asyncio.sleep(0.1)
#     #         except Exception as e:
#     #             show_er(f"[maingraph]   {e}")
#     #             time.sleep(2)
#     #             continue
#     # finally:
#     #     # 清理任务
#     #     await websocket.close()
#     #     show_lg("Connection closed")
#     # state = await realtime_news_flow_1().ainvoke(state)

#     # for s in  realtime_news_flow_1().stream(state):
#     #     print(s)
 
#     # return state.tmp_value
#     # try:
#     #     state = await realtime_news_flow_1().ainvoke(state)
#     #     await asyncio.sleep(0.1)
#     # except Exception as e:
#     #     show_er(f"[maingraph]   {e}")
#     #     time.sleep(2)
#     # finally:
#     #     # 清理任务
#     #     await websocket.close()
#     #     show_lg("Connection closed")

if __name__ == "__main__":    
    uvicorn.run(app, host="120.241.223.8", port=8765)
