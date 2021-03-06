import json, requests

url = 'http://falcon.proxyrotator.com:51337/'

apiKey1 = '8nScF6zCADybqLxBMUwYmXgoKetkQT7v'
apiKey2 = "vVe9qKMBNojcgsPaytGQETmSR3rLDbnX"

filename = "housing/spiders/proxy_list.txt"
f = open(filename, 'w+')

for i in [apiKey1, apiKey2]:

  params = dict(
      apiKey=i,
      county='US'
  )
  
  proxies = []
  
  for i in range(0, 50):
      resp = requests.get(url=url, params=params)
      data = json.loads(resp.text)
      proxies.append(data['proxy'])
  
  for m in proxies:
      print(m)
      f.write("%s\n" % m)

f.close()

