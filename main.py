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





def googleSearch(req):
    my_api_key = "AIzaSyChK4th5t6gRIkPnlOcIqwrRjCb5PneEBs"
    my_cse_id = "018139567253584497809:zpikuym7uf4"
    
    parameters = req['queryResult']['parameters']
    
    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))
    
    search_term = parameters['any']
    print('user wants to search for')
    print(search_term)
    
    try:
        results = google_search(search_term, my_api_key, my_cse_id, num=5)
    # return an error if there is an error getting the google search result
    except (ValueError, IOError) as error:
        return error

    
        
    res = "Here are the top 5 searches: "
    for result in results:
        res = res + " \n "+result['link']
    
   
    print(res)
    

    return res



# create a route for webhook
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
