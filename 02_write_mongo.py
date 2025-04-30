import sys
sys.path.append(".")
import asyncio
import warnings
warnings.filterwarnings("ignore")

from mainbrainQA_core.core.state_base import MainGraphState
from custom.workflows import kafaka_to_mongodb_flow
from mainbrainQA_core.common.utils import show_lg,show_er,show_wn,readConf
import time
# 从kafka中获取数据，写入到mongodb中，一直写。

async def main():
    loop_num = 1
    while True:
        try:
            show_lg(f"start  loop-{loop_num}")
            state = MainGraphState()
            state = await kafaka_to_mongodb_flow().ainvoke(state)
        except Exception as e:
            show_er(f"[main graph]   {e}")
            return state
        finally:
            show_lg(f"over  loop-{loop_num}")
            loop_num += 1
        time.sleep(300)
if __name__ == "__main__":
    asyncio.run(main())