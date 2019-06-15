# import flask dependencies
import json
from flask import Flask, request, make_response, jsonify
from googleapiclient.discovery import build

# initialize the flask app
app = Flask(__name__)
log = app.logger


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

# function for responses
def results():
    my_api_key = "AIzaSyChK4th5t6gRIkPnlOcIqwrRjCb5PneEBs"
    my_cse_id = "018139567253584497809:zpikuym7uf4"
    results = google_search('dialogflow', my_api_key, my_cse_id, num=5)
    
    res = "Here are the top 5 searches: "
    for result in results:
        res = res + " \n "+result['link']
    
    response ={'fulfillmentText': res}
    print(response)
    
    # build a request object
#    req = request.get_json(force=True)
# fetch action from json
#    action = req.get('queryResult').get('action')
# return a fulfillment response
    return response
# create a route for webhook


# create a route for webhook
@app.route('/', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))





# run the app
if __name__ == '__main__':
   app.run()
