import os
from typing import Dict
from abc import abstractmethod
from dotenv import  load_dotenv
from mainbrainQA_core.common.utils import show_lg,show_er
from langchain_community.chat_models import ChatTongyi,QianfanChatEndpoint
from langchain_community.embeddings import DashScopeEmbeddings,QianfanEmbeddingsEndpoint
from langchain_ollama import ChatOllama
class model_base():
    def __init__(self) -> None:
        self.load_key()

    def load_key(self):
        ret = load_dotenv("configs/keys.env")
        if ret:
            os.environ["DASHSCOPE_API_KEY"] = "sk-41e1b63e577243c5be6ca5016fb5f534"
            os.environ["IFLYTEK_SPARK_APP_ID"] = "ecca87d6"
            os.environ["IFLYTEK_SPARK_API_KEY"] = "9f481b04ee1182924861524c101a1346"
            os.environ["IFLYTEK_SPARK_API_SECRET"] = "MTY3ZGI2MDc5OTQ2NjRhMWI5YTI4YzZk"
            os.environ["QIANFAN_AK"]="IHoF78OCje0CPz4V3cbFWnqL"
            os.environ["QIANFAN_SK"]="Ff05ziSy27MYxRI9enifn03rrrhTVC2G"
            os.environ["TAVILY_KEY"]="Ftvly-E2yLBn0FTyjCvP7VlH15XsFyEnY64zgh"
            # show_er("load key failed")
        else:
            show_lg("load key success")
    def init_qfan(self):
        return {"chat":QianfanChatEndpoint(),"embed":QianfanEmbeddingsEndpoint()}
    def init_tongy(self):
        return {"chat":ChatTongyi(),"embed":DashScopeEmbeddings()}
    @abstractmethod
    def init_custom_model(self):
        ...
    def check_keys(self,name):
        show_lg(os.getenv(name))
    # def invoke(self,msg):
    #     return self.model(msg)["output"]