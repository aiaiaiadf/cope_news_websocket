from langgraph.graph import END,START,StateGraph
from mainbrainQA_core.core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from mainbrainQA_core.core.plugin_base import PluginBase
from mainbrainQA_core.core.state_base import MainGraphState
from mainbrainQA_core.common.utils import writeJson,readJson,show_db,show_lg,readConf,show_er,strptime,show_wn,show_db_p
from mainbrainQA_core.solutions.load_model.model_ollama import model_ollama
from mainbrainQA_core.common.kafka_utils import KFKConsumer
# from mainbrainQA_core.common.websocket_utils import WebSocketServer # WebSocketClient
from custom.plugin.kafaka_to_mongodb.plugin_thrid import ClassifyNews
from mainbrainQA_core.common.mongodb_utils import MongodbServer
from pymongo import MongoClient 
import time
from fastapi import websockets

class AnalysisQuery(PluginBase):    
    async def aprocess(self,state:MainGraphState):
        kafka_params = readConf("configs/kafka.conf")
        mongodb_params = readConf("configs/mongodb.conf")
        wkeys_params = readConf("configs/wkeys.conf")
        state.parameters.update({"wkeys_params":wkeys_params,"kafka_params":kafka_params,"mongodb_params":mongodb_params})
        show_db(state)
        return state
    def process(self,state:MainGraphState):
        kafka_params = readConf("configs/kafka.conf")
        mongodb_params = readConf("configs/mongodb.conf")
        wkeys_params = readConf("configs/wkeys.conf")
        state.parameters.update({"wkeys_params":wkeys_params,"kafka_params":kafka_params,"mongodb_params":mongodb_params})
        show_db(state)
        return state

    

class Cope(PluginBase):
    async def aprocess(self, state:MainGraphState):
        kafka_params = state.parameters["kafka_params"]
        mongodb_params = state.parameters["mongodb_params"]
        wkeys = state.parameters["wkeys_params"]

        mongodb_client = MongoClient(mongodb_params["mongodb_ip"])
        db = mongodb_client[mongodb_params["table_name"]]
        
        chat = model_ollama().init_custom_model("configs/ollama_classify.key")["chat"]
                
        kfk_client = KFKConsumer(kafka_params)
        kfk_client.set_bias()
        offsets = kfk_client.partition
        
        classify_news = ClassifyNews(wkeys,chat)
        try:
            for message in kfk_client.consumer:
                time.sleep(0.01)
                data = message.value.decode()
                data = await classify_news.aprocess(data)
                show_db_p(data)
                data["news"]["date"] = strptime(data["news"]["date"])
                labels = data["label"].strip()
                for label in labels.split(" "):
                    collection = db[label] 
                    collection.insert_one(
                            data,write_concern={"w":"majority","j":True}
                        )
                # try:
                #     data["news"]["date"] = strptime(data["news"]["date"])
                #     labels = data["label"].strip()
                #     for label in labels.split(" "):
                #         collection = db[label] 

                #         try:
                #             collection.insert_one(
                #                 data,write_concern={"w":"majority","j":True}
                #             )
                #         except:
                #             collection.insert_one(
                #                 data
                #             )
                # except Exception as e:
                #     show_wn(f"[mongodb write]   {e}   --   {data}")
        except  Exception as e:
            show_er(f"[nodes connect]   {e}   --   {data}")
            state.error = str(e)
        finally:
            kfk_client.consumer.commit()
            offsets = kfk_client.consumer.committed(kfk_client.tp)
            show_lg((f'Current offset for partition {kafka_params["offset"]}: {offsets}'))
            writeJson("configs/index.json",{"partition":offsets})

            mongodb_client.close()
            kfk_client.release()
        
            return state

    def process(self, state:MainGraphState):
        kafka_params = state.parameters["kafka_params"]
        mongodb_params = state.parameters["mongodb_params"]
        wkeys = state.parameters["wkeys_params"]

        mongodb_client = MongoClient(mongodb_params["mongodb_ip"])
        db = mongodb_client[mongodb_params["table_name"]]
        
        chat = model_ollama().init_custom_model("configs/ollama_classify.key")["chat"]
                
        kfk_client = KFKConsumer(kafka_params)
        offsets = kfk_client.partition
        
        classify_news = ClassifyNews(wkeys,chat)
        try:
            for message in kfk_client.consumer:
                time.sleep(0.01)
                data = message.value.decode()
                data = classify_news.process(data)
                show_db_p(data)
                data["news"]["date"] = strptime(data["news"]["date"])
                labels = data["label"].strip()
                for label in labels.split(" "):
                    collection = db[label] 
                    collection.insert_one(
                            data,write_concern={"w":"majority","j":True}
                        )
                # try:
                #     data["news"]["date"] = strptime(data["news"]["date"])
                #     labels = data["label"].strip()
                #     for label in labels.split(" "):
                #         collection = db[label] 

                #         try:
                #             collection.insert_one(
                #                 data,write_concern={"w":"majority","j":True}
                #             )
                #         except:
                #             collection.insert_one(
                #                 data
                #             )
                # except Exception as e:
                #     show_wn(f"[mongodb write]   {e}   --   {data}")
        except  Exception as e:
            show_er(f"[nodes connect]   {e}   --   {data}")
            state.error = str(e)
        finally:
            kfk_client.consumer.commit()
            offsets = kfk_client.consumer.committed(kfk_client.tp)
            show_lg((f'Current offset for partition {kafka_params["offset"]}: {offsets}'))
            writeJson("configs/index.json",{"partition":offsets})

            mongodb_client.close()
            kfk_client.release()
        
            return state


class AnalysisResults(PluginBase):
    async def aprocess(self,state:MainGraphState):
        show_lg(">>>  over~")
        return state
    def process(self,state:MainGraphState):
        show_lg(">>>  over~")
        return state