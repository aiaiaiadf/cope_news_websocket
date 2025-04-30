from langgraph.graph import END,START,StateGraph
from mainbrainQA_core.core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from mainbrainQA_core.core.plugin_base import PluginBase
from mainbrainQA_core.core.state_base import MainGraphState
from mainbrainQA_core.common.utils import writeJson,readJson,show_db,show_lg,readConf,show_er,strptime,show_wn_p,show_db_p
from mainbrainQA_core.solutions.load_model.model_ollama import model_ollama
from mainbrainQA_core.common.kafka_utils import KFKConsumer
# from mainbrainQA_core.common.websocket_utils import WebSocketServer # WebSocketClient
from custom.plugin.plugin_realtime_news_1.plugin_thrid import ClassifyNews
from mainbrainQA_core.common.mongodb_utils import MongodbServer
from pymongo import MongoClient 
import time
from fastapi import websockets


class AnalysisQuery(PluginBase):
    async def aprocess(self,state:MainGraphState):
        kafka_params = readConf("configs/kafka.conf")
        wkeys_params = readConf("configs/wkeys.conf")
        
        state.parameters.update({"wkeys_params":wkeys_params,"kafka_params":kafka_params})
        show_db(state)
        return state
    def process(self,state:MainGraphState):
        show_db_p("hello AnalysisQuery")
        kafka_params = readConf("configs/kafka.conf")
        wkeys_params = readConf("configs/wkeys.conf")
        # state.parameters.update({"wkeys_params":wkeys_params,"kafka_params":kafka_params})
        state.parameters.update({"wkeys_params":wkeys_params,"kafka_params":kafka_params})
        show_wn_p(f">1>>  {state}")
        return state

    

class Cope(PluginBase):
    def process(self, state:MainGraphState):
        show_db_p("hello Cope")
        kafka_params = state.parameters["kafka_params"]
        wkeys = state.parameters["wkeys_params"]        
        chat = model_ollama().init_custom_model("configs/ollama_classify.key")["chat"]
        bs = int(kafka_params["bs"])
        kfk_client = KFKConsumer(kafka_params)
        # offsets =  kfk_client.partition
        
        classify_news = ClassifyNews(wkeys,chat)

        show_wn_p(f">2-1>>  {state}")
        
        messages = next(kfk_client.consumer)
        if not messages:
            assert BufferError,"not get data from kafka"
            print("未收到任何消息")
        data = messages.value.decode()
        data = classify_news.process(data)
        data["news"]["date"] = strptime(data["news"]["date"])
    
        # wbt_server.send_json(data)
        state.tmp_value = data
        return state

        # # show_db_p("here   << ")
        # try:
        #     # messages = kfk_client.consumer.poll(timeout_ms=1000, max_records=bs)
        #     # for i,topic, msgs in enumerate(messages.items()):
        #     #     if msgs:
        #     #         message = next(iter(msgs))
        #     #         print(f"Received message: {message.value}")
        #     #     if i == bs-1:
        #     #         break
        #     messages = next(kfk_client.consumer)
        #     if not messages:
        #         assert BufferError,"not get data from kafka"
        #         print("未收到任何消息")
        #     data = messages.value.decode()
        #     data = classify_news.process(data)
        #     data["news"]["date"] = strptime(data["news"]["date"])
        
        #     # wbt_server.send_json(data)
        #     state.tmp_value = data
        # except Exception as e:
        #     show_er(f"[nodes connect]   {e}   --   {data}")
        #     state.error = str(e)
        # finally:
        #     # kfk_client.consumer.commit()
        #     # offsets = kfk_client.consumer.committed(kfk_client.tp)
        #     # show_lg((f'Current offset for partition {kafka_params["offset"]}: {offsets}'))
        #     # writeJson("configs/index.json",{"partition":offsets})

        #     kfk_client.release()
        #     show_wn_p(f">2-2>>  {state}")
        #     return state

    async def aprocess(self, state:MainGraphState):
        show_db_p("hello Cope")
        kafka_params = state.parameters["kafka_params"]
        wkeys = state.parameters["wkeys_params"]        
        chat = model_ollama().init_custom_model("configs/ollama_classify.key")["chat"]
        bs = int(kafka_params["bs"])
        kfk_client = KFKConsumer(kafka_params)
        # offsets =  kfk_client.partition
        
        classify_news = ClassifyNews(wkeys,chat)

        # wbt_server = state.parameters["websocket_obj"]
        show_wn_p(f">2-1>>  {state}")
        # show_db_p("here   << ")
        try:
            # messages = kfk_client.consumer.poll(timeout_ms=1000, max_records=bs)
            # for i,topic, msgs in enumerate(messages.items()):
            #     if msgs:
            #         message = next(iter(msgs))
            #         print(f"Received message: {message.value}")
            #     if i == bs-1:
            #         break
            messages = next(kfk_client.consumer)
            if not messages:
                assert BufferError,"not get data from kafka"
                print("未收到任何消息")
            data = messages.value.decode()
            data = classify_news.process(data)
            data["news"]["date"] = strptime(data["news"]["date"])
            show_db_p(data)
            # wbt_server.send_json(data)
            state.tmp_value = data
        except Exception as e:
            show_er(f"[nodes connect]   {e}   --   {data}")
            state.error = str(e)
        finally:
            # kfk_client.consumer.commit()
            # offsets = kfk_client.consumer.committed(kfk_client.tp)
            # show_lg((f'Current offset for partition {kafka_params["offset"]}: {offsets}'))
            # writeJson("configs/index.json",{"partition":offsets})

            kfk_client.release()
            show_wn_p(f">2-2>>  {state}")
            return state

    

class AnalysisResults(PluginBase):
    
    async def aprocess(self,state:MainGraphState):
        return state
    def process(self,state:MainGraphState):
        show_db_p("hello AnalysisResults")
        show_wn_p(f">3>>  {state}")
        return state