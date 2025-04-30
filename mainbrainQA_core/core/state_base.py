from pydantic import BaseModel, ConfigDict,Field
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from typing import Annotated,List,Any,Dict,Union,Set
import operator
from typing_extensions import TypedDict



class IsLoop(BaseModel):
    """是否循环"""
    isloop:bool=False


class TmpValue(BaseModel):
    """保存节点临时输出的"""
    tmpout:str=""

class MessagesState(BaseModel):
    """用户输入"""
    # user_input:List[SystemMessage, HumanMessage]= Field(default_factory=list)
    user_input:List[BaseMessage]= Field(default_factory=list)
   
    
class StrSateBase(BaseModel):
    """子图的最新响应""" 
    # latest_response:Union[Dict[str,Any],List]=None
    latest_response:str=""
    
class HistoryState(BaseModel):
    """"存储完整的对话历史"""
    # messages: Annotated[List[dict[str,Any]],operator.add]= Field(default_factory=list)
    messages: List[Union[dict[str,Any],List[str],str]]= Field(default_factory=list)
    summarize: str=""

class GlobalState(BaseModel):
    """全局环境变量"""
    tmp_value:Any = None

class RecallMsg(BaseModel):
    """处理异常的反馈信息"""
    # error:List[str] = Field(default_factory=list)
    error:str = Field(default_factory=str)
    recall:str = ""

class ParameterState(BaseModel):
    """节点需要的参数"""
    # parameters:Annotated[Dict[str, Any],Dict.update]=dict()
    parameters:Dict[str, Any]= Field(default_factory=dict)


class MainGraphState(MessagesState,
                     StrSateBase,
                     GlobalState,
                     HistoryState,
                     ParameterState,
                     IsLoop,
                     TmpValue,
                     RecallMsg):
    # def to_dict(self) -> dict:
    #     # 将对象属性转换为可序列化的字典
    #     return {
    #         'attribute1': self.attribute1,
    #         'attribute2': self.attribute2,
    #         # 其他属性...
    #     }

    # @classmethod
    # def from_dict(cls, data: dict):
    #     # 从字典创建对象实例
    #     return cls(**data)

    pass

