import os
import yaml
from datetime import datetime
from pytz import timezone



def replace_invalid_chars(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def format_date(pubtime_str):
    def get_current_beijing_date():
        tz = timezone('Asia/Shanghai')
        now = datetime.now(tz)
        year = now.year
        month = now.month
        day = now.day
        weekday_mapping = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
        weekday = weekday_mapping[now.weekday()]
        return year, month, day, weekday
    time_text = pubtime_str.replace(":", "-")
    year, month, day, weekday = get_current_beijing_date()
    return f"{year}-{month:02}-{day:02}_{weekday}_{time_text}"



def strptime(s:str):
    
    lst = s.split("_")
    # date_str = s.split("_")[0] + "_" +s.split("_")[-1]
    if len(lst) == 3:
        date_str = lst[0] + "_" + lst[-1]
    elif len(lst) == 2:
        date_str = lst[0] + "_" + lst[-1]
    else:
        assert ValueError,"not %Y-%m-%d_%H-%M or %Y-%m-%d_xxx_%H-%M"
    format = "%Y-%m-%d_%H-%M"
    dt = datetime.strptime(date_str, format)
    # show_db(type(dt))
    return dt

def timepstr(s:datetime):
    date_str = s
    format = "%Y-%m-%d_%H-%M-%S"
    dt = date_str.strftime(format)
    return dt




def now():
    tm = datetime.now().strftime("%m-%d-%y_%H-%M-%S")
    return tm

def lnow():
    tm = datetime.now().strftime("%m-%d %H:%M:%S")
    return tm




def show_db(logger,n, v=''):
    logger.debug(f"\033[33m{n} {v}\033[0m")

def show_lg(logger,n, v=''):
    logger.info(f"\033[34m{n} {v}\033[0m")

def show_er(logger,n, v='', ex=0):
    logger.error(f"\033[31m{n} {v}\033[0m")
    if ex < 0:
        exit(-1)



# def show_db(n,v=''): 
#     print(f"\033[33m[DEBUG]-[{lnow()}]  {n}  {v}\033[0m")
    
# def show_lg(n,v=''):
#     print(f"\033[34m[INFO]  {n}  {v}\033[0m")

# def show_er(n,v='',ex=0):
#     tm = lnow()
#     print(f"\033[31m[ERROR]-[{tm}]  {n}  {v}\033[0m")
#     if ex<0:
#         exit(-1)



    
def checkFileExist(pth):
    if not os.path.exists(pth):
        show_er(f"{pth} not exist")
        
def checkDir(pth):
    if not os.path.isdir(pth):
        show_er(f"{pth} not exist")
        
        
        
def readkey(pth):
    tmp_dct = dict()
    with open(pth,'r') as rf:
        lines = rf.readlines()
    for l in lines:
        if l =="" or l.startswith("#"):
            continue
        else:
            k,v = l.split("=")
            k,v = k.strip(),v.strip()
            tmp_dct[k]=v
    return tmp_dct



def readConf(path:str)->dict:
    result = dict()
    with open(path, 'r', encoding='utf-8') as rf:
        lines = rf.readlines()
        
        for line in lines:
            line = line.strip()
            b = line.startswith("#")
            if line and (not b):
                name,value = line.split("=")
                name,value = name.strip(),value.strip()
                result[name] = value
    return result

def readYaml(path:str)->dict:
    with open(path, 'r', encoding='utf-8') as rf:
        result = yaml.load(rf.read(), Loader=yaml.FullLoader)
    return result


def mkdir(dir:str):
    os.makedirs(dir,exist_ok=True)

class dictDotNotation(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

def getDir(dir:str,file:str)->str:
    tm = datetime.now().strftime("%m-%d-%y_%H-%M-%S")
    return os.path.join(dir,tm,file)


def getLatestDirectory(path):
    directories = [os.path.join(path,d) for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]    
    if not directories:
        return None
    latest_directory = max(directories, key=os.path.getctime)    
    return latest_directory

