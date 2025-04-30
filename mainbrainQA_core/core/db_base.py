#导入文本分割器
import abc
import os
from tqdm import tqdm
from pathlib import Path
try:
    from langchain_community.document_loaders import UnstructuredExcelLoader, PyPDFLoader, Docx2txtLoader, TextLoader
except:
    from langchain.document_loaders import (UnstructuredExcelLoader,
                                        PyPDFLoader,
                                        Docx2txtLoader,
                                        TextLoader)
from common.utils import now,getLatestDirectory

class db_base(object):
    map_load = {
        ".pdf":PyPDFLoader,
        ".docx":Docx2txtLoader,
        ".xlsx":UnstructuredExcelLoader,
        ".txt":TextLoader
        }
    db_dir = "dbs"
    def __init__(self,db_params:dict) -> None:
        super().__init__()
        self._parser(db_params)
        self._getPaths()
        print(self.data_paths)
   

    def _getFile(self,pth):
        suffix = os.path.splitext(pth)[-1]
        func_loader = self.map_load[suffix]
        try:
            if suffix == ".xlsx":
                loader = func_loader(pth,mode="elements")
            elif suffix == ".txt":
                loader = func_loader(pth,encoding='utf8')
            else:
                loader = func_loader(pth)
            content = loader.load()
            return content
        except Exception as err:
            print("load pdf error: ",err)
            return None
    def _parser(self,db_params:dict):
        self.data = db_params.data            #! data
        self.chunk_sz = db_params.chunk_sz    #! =400
        self.chunk_op = db_params.chunk_op    #! =20
        # self.dir = db_params.dir              #! ="../db"
    
    def _getPaths(self):
        self.data_paths=[]
        if os.path.isfile(self.data):
            self.data_paths = [self.data]
        elif os.path.isdir(self.data):
            paths = list(Path(self.data).glob("**/*.*"))
            for p in paths:
                p = str(p)
                self.data_paths+=[p]
            
        else:
            raise f"{self.data} is error"
    
    def loopEmbeddingAndVectorDB(self):   # 
        if len(self.data_paths)==0:
            assert f"{self.data_paths} is null"
        save_db_dir = os.path.join(self.db_dir,now())
        for p in tqdm(self.data_paths,desc=">> save data to DB"):
            document_txt = self._splitSentence(p)
            if document_txt == "":continue
            save_db_dir0 = os.path.join(save_db_dir,os.path.basename(os.path.splitext(p)[0]))
            self._embeddingAndVectorDB(document_txt,save_db_dir0)
        # print("done~")

    def loopVectorFromDb(self)->dict:
        save_db_dir1 = getLatestDirectory(self.db_dir) 
        save_db_dirs2 = [os.path.join(save_db_dir1,d) for d in os.listdir(save_db_dir1) if os.path.isdir(os.path.join(save_db_dir1,d))]
        db_dct_infos = dict()
        for save_db_dir in tqdm(save_db_dirs2,desc=">> upload db to host"):
            dname = os.path.basename(save_db_dir)
            vector_ = self._vectorFromDb(save_db_dir)
            db_dct_infos[dname] = vector_
        return db_dct_infos
    
    
    def _set_embed(self,model_embed):
        self.emmbeddings = model_embed

    @abc.abstractmethod
    def _splitSentence(self,pth:str):
        ... 

    @abc.abstractmethod
    def _embeddingAndVectorDB(self,docu_txt,save_db_dir):
        ...

    @abc.abstractmethod
    def _vectorFromDb(self,db_dir):
        ...


