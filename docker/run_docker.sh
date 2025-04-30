# sudo docker run -it -d \
#   -p 8000:8000 \
#   -p 27017:27017 \
#   -p 29092:29092 \
#   --link mongo:65f9dacdae36 \
#   --link kafka:fd2f7a5ba285 \
#   -v /home/cheng/about_llm/05_crawl_code/02_cope_news_server_v0.2:/work \
#   ubuntu/python:3.10-22.04_stable \
#   bin\bash
sudo docker run -itd --name test \
  ubuntu/python:3.10-22.04_stable
