import requests, json

def get_weather(address):
    url = 'http://t.weather.sojson.com/api/weather/city/'
    city = address
    f = open(r'common/thirdparty/getweather/city.json', 'rb')
    cities = json.load(f)
    city = cities.get(city)
    response = requests.get(url + city)
    d = response.json()
    results = dict()

    if(d['status'] == 200):
        results = {
            "城市":[d["cityInfo"]["parent"], d["cityInfo"]["city"]],
            "时间":[d["time"], d["data"]["forecast"][0]["week"]],
            "温度": [d["data"]["forecast"][0]["high"], d["data"]["forecast"][0]["low"]],
            "天气": d["data"]["forecast"][0]["type"]
        }
        
    s = f'当前时间为{d["time"]}，在{d["cityInfo"]["parent"],d["cityInfo"]["city"]}，天气为{d["data"]["forecast"][0]["type"]}，最高温度为{d["data"]["forecast"][0]["high"]}, 最低温度为{d["data"]["forecast"][0]["low"]}'
    results.update({"code":d['status']})
    return s

