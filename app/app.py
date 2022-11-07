from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

import requests
import json

from calendar import monthrange
import datetime
import time

app = FlaskAPI(__name__)

# must include a humanistic user agent header because wikimedia blocks requests via script
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

'''Helper functions'''
def validate_query_params():
    return True

def getDateListFromWeek(year,week):
    firstdayofweek = datetime.datetime.strptime(f'{year}-W{int(week )- 1}-1', "%Y-W%W-%w").date()
    datelist = []
    for i in range(0,7):
        day = firstdayofweek + datetime.timedelta(days=i)
        datelist.append(day.split('-'))
    return datelist


@app.route("/", methods=['GET', 'POST'])
def homepage():
    """
    Return readme here.
    """
    return "You are home."


'''Routes'''

@app.route('/pageviews/all-articles/daily/<int:year>/<int:month>/<int:day>/')
def example(year,month,day):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{year}/{month}/{day}"
    print(url)
    r = requests.get(url, headers=headers)

    data = json.loads(r.text)["items"][0]["articles"]
    print(r)

    return data

# Uses wiki's own monthly all-days endpoint, which seems to return incorrect results
@app.route('/pageviews/all-articles/monthly_native/<int:year>/<int:month>/')
def monthly_native_totals(year,month):
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikisource/all-access/{year}/{month}/all-days"
    r = requests.get(url, headers=headers)
    try:
        data = json.loads(r.text)["items"][0]["articles"]
    except Exception as e:
        return r.text
    return data

# Slow, but returns the accurate monthly total of views. Much too slow for production
@app.route('/pageviews/all-articles/monthly/<int:year>/<int:month>/')
def monthly_totals(year,month):
    monthmax = monthrange(year, month)[1]
    data_aggregate = []
    for i in range(1,monthmax+1):
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{str(year)}/{str(month).zfill(2)}/{str(i).zfill(2)}"
        print(url)
        r = requests.get(url, headers=headers)
        try:
            data = json.loads(r.text)["items"][0]["articles"]
        except Exception as e:
            print(e)
            return "There was an error processing this request"
        data_aggregate+=data

    top_views = {}
    for item in data_aggregate:
        top_views[item["article"]] = top_views.get(item["article"], 0) + item["views"]

    sorted_top_views = sorted(top_views.items(), key=lambda x: x[1], reverse=True)

    return sorted_top_views

@app.route('/pageviews/all-articles/weekly/<int:year>/<int:week>/')
def weekly_totals(year,week):
    
    data_aggregate = []
    for i in range(1,monthmax+1):
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{str(year)}/{str(month).zfill(2)}/{str(i).zfill(2)}"
        print(url)
        r = requests.get(url, headers=headers)
        try:
            data = json.loads(r.text)["items"][0]["articles"]
        except Exception as e:
            print(e)
            return "There was an error processing this request"
        return data
        data_aggregate+=data

    top_views = {}
    for item in data_aggregate:
        top_views[item["article"]] = top_views.get(item["article"], 0) + item["views"]

    sorted_top_views = sorted(top_views.items(), key=lambda x: x[1], reverse=True)

    return sorted_top_views


@app.route('/pageviews/per_article/monthly/<string:article>/<int:year>/<int:month>/')
def monthly_total_by_article(article, year,month):
    url =f" https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/Albert_Einstein/daily/2015100100/2015103100"
    # url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikisource/all-access/{year}/{month}/all-days"
    r = requests.get(url, headers=headers)
    try:
        data = json.loads(r.text)["items"][0]["articles"]
    except Exception as e:
        return r.text
    return data


if __name__ == "__main__":
    app.run(debug=True)