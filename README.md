# gt-coding-exercise

Welcome to this take home assessment! This project creates a wrapper API for the Wikimedia Pageviews API.  

## Basic Usage

This project requires Python3.6 or greater. To get started, run the following commands from project root. This will install the Python dependencies and start a local webserver at `127.0.0.1:5000`.  

```console
	pip install -r requirements.txt
	cd ./app
	python3 ./app.py
```

## Endpoints

This project features 5 types of endpoints:  
* http://127.0.0.1:5000/pageviews/all-articles/monthly/2022/10/ #Returns a list of pageviews by article for a given Month, where each list item is in the form [article, number_of_views]
* http://127.0.0.1:5000/pageviews/all-articles/weekly/2022/10/ #Returns a list of pageviews by article for a given Week, where each list item is in the form [article, number_of_views]
* http://127.0.0.1:5000/pageviews/by-article/Albert_Einstein/monthly/2022/10/ #Returns a list of total pageviews for a single article for a given Month, where each list item is in the form [article, number_of_views]
* http://127.0.0.1:5000/pageviews/by-article/Albert_Einstein/weekly/2022/10/ #Returns a list of total pageviews for a single article for a given Week, where each list item is in the form [article, number_of_views]
* http://127.0.0.1:5000/pageviews/by-article/Albert_Einstein/monthly/2022/10/monthly_high #Returns the day of the Month with the most pageviews for a single article, where each list item is in the form [date_string(YYYYMMDD), number_of_views]


**For convience, a Postman collection of all endpoints is included in this project.**
