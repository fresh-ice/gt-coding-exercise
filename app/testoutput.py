import requests

from calendar import monthrange

import json

url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/2015/10/10'



# must include a humanistic user agent header because wikimedia blocks requests via script
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

r = requests.get(url, headers=headers)
print(r)

year = 2022
month = 10

monthmax = monthrange(year, month)[1]
data_aggregate = []
for i in range(1,monthmax+1):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{year}/{month}/{str(i).zfill(2)}"
    print(url)
    r = requests.get(url, headers=headers)
    data = json.loads(r.text)["items"][0]["articles"]
    data_aggregate+=data


top_view = {}
for item in data_aggregate:
	top_view[item["article"]] = top_view.get(item["article"], 0) + item["views"]

sorted_top_views = sorted(top_view.items(), key=lambda x: x[1], reverse=True)
