import requests
API_URL = 'https://en.wikipedia.org/w/api.php'

def search_wikipedia(q, url=API_URL):
    data = {
            'action': 'query',
            'list': 'search',
            'srsearch': q,
            'format': 'json',
            'formatversion': 2
            }
    r = requests.get(url, params=data)
    j = r.json()
    search_results = j['query']['search']
    return search_results
