import json
import os

def str2dict(data:str)->dict:
    # print("result>>>   ",data)
    a,b = data.find("{"),data.rfind('}')
    data = data[a:b+1]
    data = data.replace("，",",").replace("。",".")# .replace("\"","\'")
    # print("data>>>   ",data)
    return json.loads(data)

def dropNullValue(dct:dict)->dict:
    # 取出dict中的空值对
    res = dict()
    for k,v in list(dct.items()):
        if v!="":
            res[k]=v
    return res

def duplicate_removal(messages:list[dict[str,any]]):
    # 对list中袁术去重
    tmp_lst =[]
    for msg in messages:
        tmp_dct = dict()
        for k,v in list(msg.items()):
            tmp_dct[k] = v.replace(" ","")
        if tmp_dct not in tmp_lst:
            tmp_lst.append(tmp_dct)
    return tmp_lst



def routing(state):
    b = state.isLoop
    if b:
        return 'continue'
    else:
        return "end"
    
def getLastMsg(dir:str):
    pth = os.path.join(dir,"hmsg.txt")
    lastMsg = ""
    with open(pth,'r') as rf:
        lines = rf.readlines()
        lastMsg = lines[-1]
    return lastMsg


# def saveHistory(lines):