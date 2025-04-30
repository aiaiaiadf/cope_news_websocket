from langgraph.graph import END,START,StateGraph
from mainbrainQA_core.core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from mainbrainQA_core.core.plugin_base import PluginBase
from mainbrainQA_core.core.state_base import MainGraphState
from mainbrainQA_core.common.utils import writeJson,readJson,show_db,show_lg,readConf,show_er,strptime,show_wn,show_db_p
from mainbrainQA_core.solutions.load_model.model_ollama import model_ollama
from mainbrainQA_core.common.kafka_utils import KFKConsumer
# from mainbrainQA_core.common.websocket_utils import WebSocketServer # WebSocketClient
from custom.plugin.plugin_realtime_news_2.plugin_thrid import ClassifyNews
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
        # kafka_params = readConf("configs/kafka.conf")
        # mongodb_params = readConf("configs/mongodb.conf")
        # wkeys_params = readConf("configs/wkeys.conf")
        # state.parameters.update({"wkeys_params":wkeys_params,"kafka_params":kafka_params,"mongodb_params":mongodb_params})
        # show_db_p(f"start~>>> {state}")
        return state

    

class Cope(PluginBase):
    def process(self, state:MainGraphState):
        db = state.parameters["func"]["mongo_db"]
        classify = state.parameters["func"]["classify_news"]
        wbt_server = state.parameters["func"]["wbt_server"]
        try:
            kfk_message = state.parameters["kfk_message"]   
            news_data = kfk_message.value.decode()
            news_data = classify.process(news_data)
            show_db_p(news_data)
            try:
                news_data["news"]["date"] = strptime(news_data["news"]["date"])
                labels = news_data["label"].strip()
                for label in labels.split(" "):
                    collection = db[label] 
                    try:
                        collection.insert_one(
                            news_data,write_concern={"w":"majority","j":True}
                        )
                    except:
                        collection.insert_one(
                            news_data
                        )
            except Exception as e:
                show_wn(f"[mongodb write]   {e}   --   {news_data}")
            wbt_server.send_json(news_data)
        except  Exception as e:
            show_er(f"[nodes connect]   {e}   --   {news_data}")
            state.error = str(e)
        finally:
            # show_db_p(f">>> {state}")
            return state


class AnalysisResults(PluginBase):
    async def aprocess(self,state:MainGraphState):
        show_db_p(f"over~>>> {state}")
        return state
    def process(self,state:MainGraphState):
        # show_db_p(f"over~>>> {state}")
        return state
    


"""

[DEBUG]-[04-28 14:12:19]  >>> 
error='' recall='' 
tmpout='' 
isloop=False 
parameters=
    {
    'wbt_server_params': {'uri': 'ws://120.241.223.8', 'port': '8765', 'heartbeat_interval': '5', 'heatbeat_timeout': '10', 'send_interval': '2', 'max_idle_time': '15'}, 
    'kafka_params': {'kafka_ip': 'localhost', 'port': '29092', 'acks': 'all', 'broker': 'crawl', 'topic': 'panewslab', 'partition': '0', 'auto_offset_reset': 'earliest', 'enable_auto_commit': '-1', 'group_id': 'my-group', 'offset': '0', 'heap_num': '20'}, 
    'mongodb_params': {'mongodb_ip': 'mongodb://admin:yulue123456@120.241.223.8:27017', 'table_name': 'news_2'}, 
    'wkeys_params': {'keys': 'ETF,NFT,GameFi,SocialFi,AI,DeFi,以太坊,ETH,比特币,Bitcoin'}, 
    'func': {
        'mongo_db': Database(MongoClient(host=['120.241.223.8:27017'], document_class=dict, tz_aware=False, connect=True), 'news_2'), 
        'classify_news': <custom.plugin.plugin_realtime_news_2.plugin_thrid.ClassifyNews object at 0x7f7fb53134d0>, 
        'wbt_server': <starlette.websockets.WebSocket object at 0x7f7fb53215d0>}, 
        'kfk_message': ConsumerRecord(topic='crawl', partition=0, leader_epoch=0, offset=20597, timestamp=1745609909176, timestamp_type=0, key=b'theblockbeats', 
            value=b'{"id": "529f9b63ffe602bb8ce027e", "date": "2025-04-26_\\u661f\\u671f\\u516d_01-00", "title": "\\u7f8eSEC\\u7b2c\\u4e09\\u6b21\\u52a0\\u5bc6\\u8d27\\u5e01\\u5706\\u684c\\u4f1a\\u8bae\\u73b0\\u5df2\\u5f00\\u542f\\u76f4\\u64ad", "content": "BlockBeats \\u6d88\\u606f\\uff0c4 \\u6708 26 \\u65e5\\uff0c\\u636e\\u5b98\\u65b9\\u6d88\\u606f\\uff0c\\u7f8e SEC \\u7b2c\\u4e09\\u6b21\\u52a0\\u5bc6\\u5706\\u684c\\u4f1a\\u8bae\\u5c06\\u5728\\u5317\\u4eac\\u65f6\\u95f4 4 \\u6708 26 \\u65e5\\u51cc\\u6668 1 \\u70b9\\u81f3 5 \\u70b9\\u4e3e\\u884c\\uff0c\\u73b0\\u5df2\\u5f00\\u542f\\uff0c\\u63d0\\u4f9b\\u7f51\\u7edc\\u76f4\\u64ad\\u3002\\u7f8e SEC \\u4e3b\\u5e2d Paul Atkins \\u5c06\\u51fa\\u5e2d\\u5e76\\u53d1\\u8868\\u8bb2\\u8bdd\\u3002", "website": "theblockbeats", "src": "/inclusionid/?target=https%3A%2F%2Fx.com%2FSECGov%2Fstatus%2F1915772469568323807"}', 
            headers=[], checksum=None, serialized_key_size=13, serialized_value_size=763, serialized_header_size=-1)
        }  
messages=[] summarize='' 
tmp_value=None 
latest_response='' 
user_input=[]  


"""


"""
parameters={
'wbt_server_params': {'uri': 'ws://120.241.223.8', 'port': '8765', 'heartbeat_interval': '5', 'heatbeat_timeout': '10', 'send_interval': '2', 'max_idle_time': '15'}, 'kafka_params': {'kafka_ip': 'localhost', 'port': '29092', 'acks': 'all', 'broker': 'crawl', 'topic': 'panewslab', 'partition': '0', 'auto_offset_reset': 'earliest', 'enable_auto_commit': '-1', 'group_id': 'my-group', 'offset': '0', 'heap_num': '20'}, 'mongodb_params': {'mongodb_ip': 'mongodb://admin:yulue123456@120.241.223.8:27017', 'table_name': 'news_2'}, 'wkeys_params': {'keys': 'ETF,NFT,GameFi,SocialFi,AI,DeFi,以太坊,ETH,比特币,Bitcoin'}, 'func': {'mongo_db': Database(MongoClient(host=['120.241.223.8:27017'], document_class=dict, tz_aware=False, connect=True), 'news_2'), 'classify_news': <custom.plugin.plugin_realtime_news_2.plugin_thrid.ClassifyNews object at 0x7f120c6860d0>, 'wbt_server': <starlette.websockets.WebSocket object at 0x7f120b175090>}, 'kfk_message': ConsumerRecord(topic='crawl', partition=0, leader_epoch=0, offset=20597, timestamp=1745609909176, timestamp_type=0, key=b'theblockbeats', value=b'{"id": "529f9b63ffe602bb8ce027e", "date": "2025-04-26_\\u661f\\u671f\\u516d_01-00", "title": "\\u7f8eSEC\\u7b2c\\u4e09\\u6b21\\u52a0\\u5bc6\\u8d27\\u5e01\\u5706\\u684c\\u4f1a\\u8bae\\u73b0\\u5df2\\u5f00\\u542f\\u76f4\\u64ad", "content": "BlockBeats \\u6d88\\u606f\\uff0c4 \\u6708 26 \\u65e5\\uff0c\\u636e\\u5b98\\u65b9\\u6d88\\u606f\\uff0c\\u7f8e SEC \\u7b2c\\u4e09\\u6b21\\u52a0\\u5bc6\\u5706\\u684c\\u4f1a\\u8bae\\u5c06\\u5728\\u5317\\u4eac\\u65f6\\u95f4 4 \\u6708 26 \\u65e5\\u51cc\\u6668 1 \\u70b9\\u81f3 5 \\u70b9\\u4e3e\\u884c\\uff0c\\u73b0\\u5df2\\u5f00\\u542f\\uff0c\\u63d0\\u4f9b\\u7f51\\u7edc\\u76f4\\u64ad\\u3002\\u7f8e SEC \\u4e3b\\u5e2d Paul Atkins \\u5c06\\u51fa\\u5e2d\\u5e76\\u53d1\\u8868\\u8bb2\\u8bdd\\u3002", "website": "theblockbeats", "src": "/inclusionid/?target=https%3A%2F%2Fx.com%2FSECGov%2Fstatus%2F1915772469568323807"}', headers=[], checksum=None, serialized_key_size=13, serialized_value_size=763, serialized_header_size=-1
)
}  

"""