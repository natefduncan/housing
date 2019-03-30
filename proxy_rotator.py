import json, requests

url = 'http://falcon.proxyrotator.com:51337/'

params = dict(
    apiKey='8nScF6zCADybqLxBMUwYmXgoKetkQT7v',
    county='US'
)

proxies = []

for i in range(0, 30):
    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)
    proxies.append(data['proxy'])

filename = "housing/spiders/proxy_list.txt"

f = open(filename, 'a+')

for m in proxies:
    print(m)
    f.write("%s\n" % m)
f.close()

