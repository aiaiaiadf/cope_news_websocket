from kafka import KafkaProducer,KafkaConsumer, TopicPartition
from mainbrainQA_core.common.utils import show_db
import os
from mainbrainQA_core.common.utils import readJson
import uuid

class KFKConsumer():
    def __init__(self,kfk_params:dict):
        self._parser(kfk_params)
        
        self.consumer = KafkaConsumer(
            bootstrap_servers=f"{self.ip}:{self.port}",
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=self.enable_auto_commit,
            group_id= str(uuid.uuid1()),# self.group_id,
            # value_deserializer=lambda x: x.decode('utf-8')
            )
    def set_bias(self): 
        self.tp = TopicPartition(self.broker,0)
        # show_db(f"{self.tp}     {self.partition}<<<< ")
        self.consumer.assign([self.tp])
        self.consumer.seek(self.tp,self.partition)

    def _parser(self,kfk_params):
        self.ip = kfk_params['kafka_ip']
        self.port = kfk_params['port']
        self.acks = kfk_params['acks']
        self.broker = kfk_params['broker']
        self.topic = kfk_params['topic']
        
        if os.path.exists("configs/index.json"):
            self.partition = int(readJson("configs/index.json")["partition"])
        else:
            self.partition = int(kfk_params['partition'])
       
        self.auto_offset_reset=kfk_params['auto_offset_reset'],
        b = False if int(kfk_params["enable_auto_commit"]) <0 else True
        self.enable_auto_commit = b
        self.group_id= None # kfk_params['group_id']
        self.heap_num = int(kfk_params['heap_num'])


    def release(self):
        self.consumer.close()
        # self.produce.close()




class KFKProducer():
    def __init__(self,kfk_params:dict):
        self._parser(kfk_params)
        # bootstrap_servers='localhost:29092'
        # show_db(f"{self.ip}:{self.port}")
        self.produce = KafkaProducer(
            bootstrap_servers=f"{self.ip}:{self.port}",
            acks=self.acks)
    def _parser(self,kfk_params):
        self.ip = kfk_params['kafka_ip']
        self.port = kfk_params['port']
        self.acks = kfk_params['acks']
        self.broker = kfk_params['broker']
        self.topic = kfk_params['topic']
        self.partition = int(kfk_params['partition'])
    def process(self,data):
        data_ = str(data).encode()
        # show_db(data['webset'].encode())
        self.produce.send(self.broker,key=data['webset'].encode(),value=data_,partition=self.partition)
        self.produce.flush()
    def release(self):
        self.produce.close()