from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

import requests
import json

from calendar import monthrange
import datetime
import time

import markdown

import asyncio
import aiohttp

app = FlaskAPI(__name__)

''' Globals '''
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# must include a user agent header because wikimedia blocks requests via script


'''Helper functions'''


def validate_query_params():
    return True


def getDateListFromWeek(year, week):
    firstdayofweek = datetime.datetime.strptime(f'{year}-W{int(week )- 1}-1', "%Y-W%W-%w").date()
    datelist = []
    for i in range(0, 7):
        day = firstdayofweek + datetime.timedelta(days=i)
        datelist.append(str(day).split('-'))
        print(day)
    print(datelist)
    return datelist


def getDateListFromMonth(year, month):
    monthmax = monthrange(year, month)[1]
    datelist = []
    for i in range(1, monthmax+1):
        datelist.append([str(year), str(month), str(i)])
    print(datelist)
    return datelist


async def get_async(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            return resp
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def aggregate_responses(urls):
    data_aggregate = []

    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get_async(url, session) for url in urls])
        for chunk in ret:
            data = json.loads(chunk.decode('utf-8'))
            print("Data is:", data)
            data_aggregate+=data["items"][0]["articles"]

        top_view = {}
        for item in data_aggregate:
            top_view[item["article"]] = top_view.get(item["article"], 0) + item["views"]

        sorted_top_views = sorted(top_view.items(), key=lambda x: x[1], reverse=True)
        return sorted_top_views


'''Routes'''


@app.route("/", methods=['GET'])
def homepage():
    """
    Return readme here.
    """
    with open("../README.md", "r") as f:
        html = markdown.markdown(f.read())
    return html


@app.route('/pageviews/all-articles/daily/<int:year>/<int:month>/<int:day>/')
def example(year, month, day):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{year}/{month}/{day}/"
    r = requests.get(url, headers=HEADERS)

    data = json.loads(r.text)["items"][0]["articles"]
    print(r)

    return data


# Uses wiki's own monthly all-days endpoint, which seems to return incorrect results
@app.route('/pageviews/all-articles/monthly_native/<int:year>/<int:month>/')
def monthly_native_totals(year,month):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikisource/all-access/{year}/{month}/all-days"
    r = requests.get(url, headers=HEADERS)
    try:
        data = json.loads(r.text)["items"][0]["articles"]
    except Exception as e:
        return r.text
    return data


# Slow, but returns the accurate monthly total of views.
# Much too slow for production
@app.route('/pageviews/all-articles/monthly/<int:year>/<int:month>/')
def monthly_totals(year, month):
    monthmax = monthrange(year, month)[1]
    data_aggregate = []
    for i in range(1, monthmax+1):
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{str(year)}/{str(month).zfill(2)}/{str(i).zfill(2)}"
        r = requests.get(url, headers=HEADERS)
        try:
            data = json.loads(r.text)["items"][0]["articles"]
        except Exception as e:
            print(e)
            return "There was an error processing this request"
        data_aggregate += data

    top_views = {}
    for item in data_aggregate:
        top_views[item["article"]] = top_views.get(item["article"], 0) + item["views"]

    sorted_top_views = sorted(top_views.items(), key=lambda x: x[1], reverse=True)

    return sorted_top_views


@app.route('/pageviews/all-articles/weekly/<int:year>/<int:week>/')
def weekly_totals(year, week):
    print("weekly")
    date_list = getDateListFromWeek(year, week)
    print(date_list)
    data_aggregate = []
    for day in date_list:
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{str(day[0])}/{str(day[1]).zfill(2)}/{str(day[2]).zfill(2)}"
        print("url", url)
        r = requests.get(url, headers=HEADERS)
        try:
            data = json.loads(r.text)["items"][0]["articles"]
        except Exception as e:
            print(e)
            return "There was an error processing this request"
        data_aggregate += data

    top_views = {}
    for item in data_aggregate:
        top_views[item["article"]] = top_views.get(item["article"], 0) + item["views"]

    sorted_top_views = sorted(top_views.items(), key=lambda x: x[1], reverse=True)

    return sorted_top_views


@app.route('/pageviews/by-article/<string:article>/monthly/<int:year>/<int:month>/<string:max_views>')
@app.route('/pageviews/by-article/<string:article>/monthly/<int:year>/<int:month>/')
def monthly_total_by_article(article, year, month, max_views=False):
    date_list = getDateListFromMonth(year, month)
    data_aggregate = []
    begin_day = date_list[0]
    end_day = date_list[-1]
    date_range = f"{begin_day[0]+begin_day[1].zfill(2)+begin_day[2].zfill(2)}00/{end_day[0]+end_day[1].zfill(2)+end_day[2].zfill(2)}00"

    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/daily/{date_range}"

    r = requests.get(url, headers=HEADERS)
    try:
        data = json.loads(r.text)["items"]
    except Exception as e:
        print("There was an error processing upstream response", e)
        return "There was an error processing this request"
    data_aggregate += data

    monthly_high = [0, 0]
    top_views = {}
    for item in data_aggregate:
        timestamp = item["timestamp"]
        top_views[item["article"]] = top_views.get(item["article"], 0) + item["views"]
        if item["views"] > monthly_high[1]:
            monthly_high = [timestamp[:-2], item["views"]]

    sorted_top_views = sorted(top_views.items(), key=lambda x: x[1], reverse=True)

    if max_views == 'monthly_high':
        return [monthly_high]

    return sorted_top_views


@app.route('/pageviews/by-article/<string:article>/weekly/<int:year>/<int:week>/')
def weekly_total_by_article(article, year, week):
    date_list = getDateListFromWeek(year, week)
    data_aggregate = []
    begin_day = date_list[0]
    end_day = date_list[-1]
    date_range = f"{begin_day[0]+begin_day[1].zfill(2)+begin_day[2].zfill(2)}00/{end_day[0]+end_day[1].zfill(2)+end_day[2].zfill(2)}00"
    print(date_range)
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/daily/{date_range}"

    print(url)
    r = requests.get(url, headers=HEADERS)
    try:
        data = json.loads(r.text)["items"]
    except Exception as e:
        print("There was an error processing upstream response", e)
        return "There was an error processing this request"
    data_aggregate+=data

    print("dataagrerga", data_aggregate)

    top_views = {}
    for item in data_aggregate:
        top_views[item["article"]] = top_views.get(item["article"], 0) + item["views"]

    print(top_views)
    sorted_top_views = sorted(top_views.items(), key=lambda x: x[1], reverse=True)
    return sorted_top_views


# Switch aggregators to use async, which increases performance by 21x
@app.route('/v2/pageviews/all-articles/monthly/<int:year>/<int:month>/')
def async_monthly_totals(year, month):
    urls = [f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{str(day[0])}/{str(day[1]).zfill(2)}/{str(day[2]).zfill(2)}" for day in getDateListFromMonth(year, month)]
    return asyncio.run(aggregate_responses(urls))


@app.route('/v2/pageviews/all-articles/weekly/<int:year>/<int:week>/')
def async_weekly_totals(year, week):
    urls = [f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{str(day[0])}/{str(day[1]).zfill(2)}/{str(day[2]).zfill(2)}" for day in getDateListFromWeek(year, week)]
    return asyncio.run(aggregate_responses(urls))


if __name__ == "__main__":
    app.run(debug=True)