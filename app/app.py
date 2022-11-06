from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

import requests
import json

from calendar import monthrange

app = FlaskAPI(__name__)

# must include a humanistic user agent header because wikimedia blocks requests via script
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

notes = {
    0: 'do the shopping',
    1: 'build the codez',
    2: 'paint the door',
}

def note_repr(key):
    return {
        'url': request.host_url.rstrip('/') + url_for('notes_detail', key=key),
        'text': notes[key]
    }


@app.route("/", methods=['GET', 'POST'])
def notes_list():
    """
    List or create notes.
    """
    if request.method == 'POST':
        note = str(request.data.get('text', ''))
        idx = max(notes.keys()) + 1
        notes[idx] = note
        return note_repr(idx), status.HTTP_201_CREATED

    # request.method == 'GET'
    return [note_repr(idx) for idx in sorted(notes.keys())]


@app.route("/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def notes_detail(key):
    """
    Retrieve, update or delete note instances.
    """
    if request.method == 'PUT':
        note = str(request.data.get('text', ''))
        notes[key] = note
        return note_repr(key)

    elif request.method == 'DELETE':
        notes.pop(key, None)
        return '', status.HTTP_204_NO_CONTENT

    # request.method == 'GET'
    if key not in notes:
        raise exceptions.NotFound()
    return note_repr(key)

def validate_query_params():
    return True

@app.route('/pageviews/<int:year>/<int:month>/<int:day>/')
def example(year,month,day):
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{year}/{month}/{day}"
    print(url)
    r = requests.get(url, headers=headers)

    data = json.loads(r.text)["items"][0]["articles"]



    print(r)


    return data

# Uses wiki's own monthly all-days endpoint, which seems to return incorrect results
@app.route('/pageviews/monthly_native/<int:year>/<int:month>/')
def monthly_native_totals(year,month):
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikisource/all-access/{year}/{month}/all-days"
    r = requests.get(url, headers=headers)
    try:
        data = json.loads(r.text)["items"][0]["articles"]
    except Exception as e:
        return r.text
    return data

# Slow, but returns the accurate monthly total of views. Much too slow for production
@app.route('/pageviews/monthly/<int:year>/<int:month>/')
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
        return data
        data_aggregate+=data

    top_views = {}
    for item in data_aggregate:
        top_views[item["article"]] = top_views.get(item["article"], 0) + item["views"]

    sorted_top_views = sorted(top_views.items(), key=lambda x: x[1], reverse=True)

    return sorted_top_views


if __name__ == "__main__":
    app.run(debug=True)