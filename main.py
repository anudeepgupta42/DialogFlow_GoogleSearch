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
       
    res = []
    for result in results:
        res.append(result['link'])
    
    response_json = {
      "fulfillmentMessages": [
          {
            "platform": "ACTIONS_ON_GOOGLE",
            "simpleResponses": {
              "simpleResponses": [
                { "textToSpeech": "Below are your top five search results "}
              ]
            }
          },
          {
            "platform": "ACTIONS_ON_GOOGLE",
            "linkOutSuggestion": {
              "destinationName": "Search result 1",
              "uri": res[0]
            }
          },
    	  {
            "platform": "ACTIONS_ON_GOOGLE",
            "linkOutSuggestion": {
              "destinationName": "Search result 2",
              "uri": res[1]
            }
          },
        {
            "platform": "ACTIONS_ON_GOOGLE",
            "linkOutSuggestion": {
              "destinationName": "Search result 3",
              "uri": res[2]
            }
          },
    	  {
            "platform": "ACTIONS_ON_GOOGLE",
            "linkOutSuggestion": {
              "destinationName": "Search result 4",
              "uri": res[3]
            }
          },
         {
            "platform": "ACTIONS_ON_GOOGLE",
            "linkOutSuggestion": {
              "destinationName": "Search result 5",
              "uri": res[4]
            }
          },
          {
            "text": {
              "text": [
                "Below are your top five search results:" +"\n"+res[0] +"\n"+res[1] +"\n"+res[2] +"\n"+res[3] +"\n"+res[4]
              ]
            }
          }
        ]
    }
    print(response_json)
    print("\n")
    print(res)        
    return response_json


@app.route('/', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    if action == 'googlesearch':
        response_json = googleSearch(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)

    return make_response(jsonify(response_json))

# run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
