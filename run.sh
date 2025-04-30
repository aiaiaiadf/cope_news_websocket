# nohup python main.py > websocket.log 2>&1 & echo $1 > websocket.pid 
# nohup uvicorn more_news:app --reload > more_news.log 2>&1 & echo $1 > more_news.pid
# uvicorn realtime_news:app --reload --host 120.241.223.8 --port 8765 
# uvicorn cope_realtime_news:app --host 120.241.223.8 --port 8765 --reload --timeout-keep-alive 10
# uvicorn realtime_news:app --reload --host 120.241.223.8 --port 8765  --limit-concurrency 20 



set -e
bash 01.sh &
bash 02.sh &
bash 03.sh &