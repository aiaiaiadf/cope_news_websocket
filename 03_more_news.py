import json
import uvicorn
from pydantic import BaseModel
from datetime import datetime
from pymongo import MongoClient
from fastapi import FastAPI, Body,Path,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mainbrainQA_core.common.utils import show_db,timepstr,readConf,strptime

# des  获取更多的新闻，支持两个中各，上划和下拉两个post请求

# uvicorn more_news:app --reload
# uvicorn 03_more_news:app --host 120.241.223.8 --port 8000 --reload


# http://120.241.223.8:8766/docs
# up down
# {
#   "date": "2025-04-15_15-51",
#   "max_num": "10",
#   "label": "all"
#   "mode": "up"   "down"
# }

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class RollData(BaseModel):
    date:str
    max_num:str
    label:str
    mode:str


@app.post("/news/more_news")
def post_more_news(
    items: RollData = Body(...)
    ):

    mongo_msg = readConf("configs/retrieve_mongodb.conf")
    cutoff_date = strptime(items.date)
    max_num = int(items.max_num)

    client = MongoClient(mongo_msg["mongodb_ip"]) 
    db = client[mongo_msg["table_name"]]

    show_db(items)
    if items.mode not in ["up", "down"]:
        raise HTTPException(status_code=400, detail="Invalid direction")
    if items.label == "all":
        def merge_all_collections_to_cache():
            collection_names = db.list_collection_names()
            # print("collection_names   ",collection_names)
            cache = []
            for collection_name in collection_names:
                source_collection = db[collection_name]
                # print(f"正在读取集合: {collection_name}")
                cursor = source_collection.find({})
                for doc in cursor:
                    cache.append(doc)
            return cache

        def query_and_sort_data(cache, target_date, limit=10):
            # for doc in cache:
            #     print(doc)
            if items.mode == "up":
                filtered_data = [doc for doc in cache if 'date' in doc["news"] and isinstance(doc["news"]['date'], datetime) and doc["news"]['date'] > target_date]
            elif items.mode == "down":
                filtered_data = [doc for doc in cache if 'date' in doc["news"] and isinstance(doc["news"]['date'], datetime) and doc["news"]['date'] < target_date]
            show_db(filtered_data)
            sorted_data = sorted(filtered_data, key=lambda x: x["news"]['date'])
            
            return sorted_data[:limit]
            
        cache = merge_all_collections_to_cache()
        results = query_and_sort_data(cache, cutoff_date, limit=max_num)
        # print(results)
    else:
        collection = db[items.label]
        
        if items.mode == "up":
            query = {
                    # 'category': items.label,
                    'news.date': {'$lt': cutoff_date}}
        elif items.mode == "down":
            query = {
                    # 'category': items.label,
                    'news.date': {'$lt': cutoff_date}}
        results = collection.find(query).sort('news.date', -1).limit(max_num)
    # 生成结果
    outs = []
    for result in results:
        show_db(result)
        result["news"]["date"] = timepstr(result["news"]["date"])
        result["_id"] = str(result["_id"])
        outs.append(result)
        show_db(result)
    # resout = [r for r in results]
    client.close()
    return {"results":outs}


if __name__ == "__main__":
    # 设置主机为0.0.0.0，允许外部访问；端口号为8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
    