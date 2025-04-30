
from custom.prompt.prompt_vector import classify_msg,classify_prompt
from mainbrainQA_core.common.llm_utils import str2dict
from mainbrainQA_core.common.utils import replace_invalid_chars,show_er,show_db_p
from mainbrainQA_core.solutions.load_model.model_ollama import model_ollama

class ClassifyNews():
    def __init__(self,filter_params:dict,chat_model):
        self.chat = chat_model
        self.wkeys = filter_params["keys"].split(",")
        self.classify_prompt = classify_prompt
        self.classify_prompt.set_system_msg(classify_msg)
        self.chat = model_ollama().init_custom_model("configs/ollama_classify.key")["chat"]
    def process(self,data:str):
        tmp_labels = ""
        try:
            data_dct = str2dict(data.replace("'",'"'))
        except:
            data_dct = str2dict(data)
        check_data = data_dct["title"] + data_dct["content"]
        b0 = True
        for wkey in self.wkeys:
            if wkey in check_data:
                b0 = False
                wkey = "Bitcoin" if wkey  == "比特币" else wkey
                wkey = "ETH" if wkey  == "以太坊" else wkey
                tmp_labels += wkey+" "
        if b0:
            self.classify_prompt.set_human_msg(check_data)
            msg = self.classify_prompt.get_messages()
            tmp_labels = self.chat.invoke(msg).content
            for i in ['ck','hg','other']:
                if i in tmp_labels:
                    tmp_labels = i
                    break
        tmp_labels = tmp_labels.strip()
        data_dct["date"] = data_dct["date"].split("_")[0] +"_"+data_dct["date"].split("_")[-1]
        tmp_labels = tmp_labels.strip()
        out_dct = dict(label=tmp_labels, news=data_dct,next="")  
        # show_db_p(f">>>>   {out_dct}")
        #! 格式示例
        # {
        # 	"label":"hg",
        # 	"news":{
        # 		'date': '2025-04-15_星期二_16-24', 
        # 		'title': '分析师Eugene：加密市场仍处于熊市，倾向于在反弹时寻找山寨币的做空机会', 
        # 		'content': 'PANews 4月15日消息，加密分析师Eugene表示，由于加密市场价格驱动因素从行业特定转向宏观经济，他在过去一个月的市场判断未能奏效。他曾认为自己对市场走势有敏锐的洞察力，但最近感觉有所偏离。自三月以来，他的交易量较之前平均下降了60-70%，基本处于盈亏平衡状态。Eugene计划继续保持低交易量和紧止损，直到市场走势再次对他有利。他强调，加密市场的宏观趋势未变，仍处于熊市，他倾向于在熊市反弹时寻找非BTC的山寨币做空机会，因为这些币种尚未达到深度价值区间。', 
        # 		'webset': 'panewslab', 
        # 		'src': 'https://www.panewslab.com//zh/sqarticledetails/jwiz749j.html'
        # 	}
        # 	"next":""
        # }
        #! 数据保存到本地的代码，不要删除
        # for k in tmp_labels.split(" "):
        #     tmp = data_dct["date"].split("_")[0]
        #     # save_txt_dir =  os.path.join("news",data_dct["webset"],tmp,k)
        #     save_txt_dir =  os.path.join("news",data_dct["website"],tmp,k)
        #     try:
        #         os.makedirs(save_txt_dir,exist_ok=True)
        #         filename = replace_invalid_chars(data_dct["title"][:10])+".txt"
        #         with open(os.path.join(save_txt_dir,filename),"a+") as af:
        #             af.write(data)
        #     except Exception as e:
        #         show_er(f"[cope_news_inner]   {e}")
        #         show_er(data)
        return out_dct
    async def aprocess(self,data:str):
        tmp_labels = ""
        try:
            data_dct = str2dict(data.replace("'",'"'))
        except:
            data_dct = str2dict(data)
        check_data = data_dct["title"] + data_dct["content"]
        b0 = True
        for wkey in self.wkeys:
            if wkey in check_data:
                b0 = False
                wkey = "Bitcoin" if wkey  == "比特币" else wkey
                wkey = "ETH" if wkey  == "以太坊" else wkey
                tmp_labels += wkey+" "
        if b0:
            self.classify_prompt.set_human_msg(check_data)
            msg = self.classify_prompt.get_messages()
            tmp_labels = await self.chat.ainvoke(msg)
            tmp_labels = tmp_labels.content.strip()
            for i in ['ck','hg','other']:
                if i in tmp_labels:
                    tmp_labels = i
                    break
      
        data_dct["date"] = data_dct["date"].split("_")[0] +"_"+data_dct["date"].split("_")[-1]
        out_dct = dict(label=tmp_labels, news=data_dct,next="")  
        # show_db_p(f">>>>   {out_dct}")
        #! 格式示例
        # {
        # 	"label":"hg",
        # 	"news":{
        # 		'date': '2025-04-15_星期二_16-24', 
        # 		'title': '分析师Eugene：加密市场仍处于熊市，倾向于在反弹时寻找山寨币的做空机会', 
        # 		'content': 'PANews 4月15日消息，加密分析师Eugene表示，由于加密市场价格驱动因素从行业特定转向宏观经济，他在过去一个月的市场判断未能奏效。他曾认为自己对市场走势有敏锐的洞察力，但最近感觉有所偏离。自三月以来，他的交易量较之前平均下降了60-70%，基本处于盈亏平衡状态。Eugene计划继续保持低交易量和紧止损，直到市场走势再次对他有利。他强调，加密市场的宏观趋势未变，仍处于熊市，他倾向于在熊市反弹时寻找非BTC的山寨币做空机会，因为这些币种尚未达到深度价值区间。', 
        # 		'webset': 'panewslab', 
        # 		'src': 'https://www.panewslab.com//zh/sqarticledetails/jwiz749j.html'
        # 	}
        # 	"next":""
        # }
        #! 数据保存到本地的代码，不要删除
        # for k in tmp_labels.split(" "):
        #     tmp = data_dct["date"].split("_")[0]
        #     # save_txt_dir =  os.path.join("news",data_dct["webset"],tmp,k)
        #     save_txt_dir =  os.path.join("news",data_dct["website"],tmp,k)
        #     try:
        #         os.makedirs(save_txt_dir,exist_ok=True)
        #         filename = replace_invalid_chars(data_dct["title"][:10])+".txt"
        #         with open(os.path.join(save_txt_dir,filename),"a+") as af:
        #             af.write(data)
        #     except Exception as e:
        #         show_er(f"[cope_news_inner]   {e}")
        #         show_er(data)
        return out_dct
    