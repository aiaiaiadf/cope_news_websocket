from pymongo import MongoClient 


class MongodbServer():
    def __init__(self,params_dct):
        self._parser(params_dct)
        self.client = MongoClient(self.db)
        db = self.client[self.tabel_name]
        self.collection =  db[self.sheet_name]

    def _parser(self,params_dct:dict):
        self.db = params_dct["mongodb_ip"]
        self.tabel_name = params_dct["table_name"]
        if params_dct.get("sheet_name"):
            self.sheet_name = params_dct["sheet_name"]
        else:
            self.sheet_name = "all"
            
    def process(self,data):
        assert isinstance(data,dict),TypeError
        try:
            self.collection.insert_one(
                data,write_concern={"w":"majority","j":True}
            )
        except:
            self.collection.insert_one(
                data
            )
    def release(self):
        self.client.close()
        