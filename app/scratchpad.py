import requests

from calendar import monthrange

import json

url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/2015/10/10'



# must include a humanistic user agent header because wikimedia blocks requests via script
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def testRequests():
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



#test Async

import asyncio
import aiohttp
import time

year = 2022
month = 10

monthmax = monthrange(year, month)[1]

urls = [f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{year}/{month}/{str(i).zfill(2)}" for i in range(1,monthmax+1)]
print(urls)

async def get(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))

async def main(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])
        print(ret)
    print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))



async def get_async(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            return resp
            # print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))

async def aggregate_responses(urls):
    data_aggregate = []

    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get_async(url, session) for url in urls])
        # data_aggregate = [json.loads(chunk.decode('utf-8'))["items"][0]["articles"] for chunk
        # in ret]

        for chunk in ret:
        	data = json.loads(chunk.decode('utf-8'))
        	print("Data is:", data)
        	data_aggregate+=data["items"][0]["articles"]
        	break
        # 	print(type(chunk))
        # 	print(chunk.decode('utf-8'))
        # 	break
        # print(type(ret))
        # print(len(ret))
        # print(ret[0])
        # print(len(ret[0]))

        top_view = {}
        for item in data_aggregate:
            top_view[item["article"]] = top_view.get(item["article"], 0) + item["views"]



        sorted_top_views = sorted(top_view.items(), key=lambda x: x[1], reverse=True)
        print(sorted_top_views)


    print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))


start = time.time()
asyncio.run(aggregate_responses(urls))
end = time.time()

print("Took {} seconds to pull {} websites.".format(end - start, len(urls)))