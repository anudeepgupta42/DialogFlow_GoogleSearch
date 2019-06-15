# import flask dependencies
import json
from flask import Flask, request, make_response, jsonify
from googleapiclient.discovery import build
from config import (CSE_API_KEY, CSE_ID)
# initialize the flask app
app = Flask(__name__)
log = app.logger


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def googleSearch(req):
    my_api_key = CSE_API_KEY
    my_cse_id = CSE_ID
    
    parameters = req['queryResult']['parameters']
    
    search_term = parameters['any']

    try:
        results = google_search(search_term, my_api_key, my_cse_id, num=5)
    # return an error if there is an error getting the google search result
    except (ValueError, IOError) as error:
        return error
       
    res = "Here are the top 5 searches: "
    for result in results:
        res = res + " \n "+result['link']
    
    return res


@app.route('/', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    if action == 'googlesearch':
        res = googleSearch(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)
    print('Response: ' + res)

    return make_response(jsonify({'fulfillmentText': res}))

# run the app
if __name__ == '__main__':
   app.run()
