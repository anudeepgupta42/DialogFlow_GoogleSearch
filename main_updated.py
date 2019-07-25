# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask,jsonify,request,make_response
import googlemaps
import pprint
import time
import json
import pandas as pd
import pandas_gbq
from googleapiclient.discovery import build
from config import (CSE_API_KEY, CSE_ID)


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
log = app.logger
#Declare the API key
API_KEY = 'AIzaSyAdH-a3k5fBy-_DyNhygTAtaqzNkhw_rVk'

my_fields = ['name','formatted_phone_number','formatted_address','rating','website','vicinity','international_phone_number']
gmaps = googlemaps.Client(key = API_KEY)
results = []
#global results
results_places = []
#global results_places
latlong = 0
type1 = 0


def main_api_places(latlong,type1):
    place_id = []
    places_result = gmaps.find_place(input = latlong,input_type = 'textquery')
    for x in places_result['candidates']:
        place_id = x['place_id']
    place_details = gmaps.place(place_id = place_id)
    coordinates = place_details['result']['geometry']['location']
    lat_long = (coordinates['lat'],coordinates['lng'])
    places_result = gmaps.places_nearby(location = lat_long,radius = 400,type = type1)
    places_endresults = []
    for x in places_result['results']:
        places_details = gmaps.place(place_id = x['place_id'], fields = my_fields)
        places_endresults.append(places_details['result']['name'])
    return(places_endresults)

def main_api_places_id(latlong,type1):
    place_id = []
    places_result = gmaps.find_place(input = latlong,input_type = 'textquery')
    for x in places_result['candidates']:
        place_id = x['place_id']
    place_details = gmaps.place(place_id = place_id)
    coordinates = place_details['result']['geometry']['location']
    lat_long = (coordinates['lat'],coordinates['lng'])
    places_result = gmaps.places_nearby(location = lat_long,radius = 400,type = type1)
    places_details1 = []
    for x in places_result['results']:
      places_details1.append(x['place_id'])
    return places_details1

def call_api(req):
    parameters = req['queryResult']['parameters']
    global latlong
    latlong = parameters['geo-city']
    global type1
    type1 = parameters['Type_of_establishments']
    global results
    results = main_api_places(latlong, type1)
    global results_places
    results_places = main_api_places_id(latlong,type1)
    
 
    res = "Here are the top search results :"
    for result in results : 
        res = res + "\n" +result
    
    res_1 = {'fulfillmentText': res}
    return res_1

results = main_api_places(latlong, type1)
results_places = main_api_places_id(latlong,type1)

def call_api2(req):
    parameters = req['queryResult']['parameters']
    place_name = parameters['any']
    new_dict = dict(zip(results, results_places))
    id = new_dict[place_name]
    gm = (gmaps.place(place_id = id, fields = my_fields))

    a = gm['result']['formatted_phone_number']
    b = gm['result']['formatted_address']
    c = gm['result']['name']
    e = gm['result']['rating']
    f = gm['result']['vicinity']
    g = gm['result']['international_phone_number']
    
    d = 'Name : '+c+'\nPhone Number : '+a+'\nAddress : '+b+'\nRating : '+str(e)+'\nVicinity : '+f+'\nInternational Phone Number : '+g
    
    res_2 = {'fulfillmentText': d}
    
    return res_2

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
    "fulfillmentText": "This is a text response",
    "fulfillmentMessages": [],
    "source": "example.com",
    "payload": {
        "google": {
            "expectUserResponse": True,
            "richResponse": {
                "items": [
                    {
                        "simpleResponse": {
                            "textToSpeech": "Please find below your top 5 searches:"
                        }
                    },
					{
					  "carouselBrowse": {
						"items": [
						  {
							"title": res[0][8:20] + '...',
							"openUrlAction": {
							  "url": res[0]
							}
						  },
						  {
							"title": res[1][8:20] + '...',
							"openUrlAction": {
							  "url": res[1]
							}
						  },
                    				{
							"title": res[2][8:20] + '...',
							"openUrlAction": {
							  "url": res[2]
							}
						  },
						  {
							"title": res[3][8:20] + '...',
							"openUrlAction": {
							  "url": res[3]
							}
						  },
                    						  {
							"title": res[4][8:20] + '...',
							"openUrlAction": {
							  "url": res[4]
							}
						  }
						]
					  }
					}
                ]
            }
        }
    },
    "outputContexts": [],
    "followupEventInput": {}
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
    res = []      
    if action == 'input.welcome':
        res = call_api(req)
    elif action == 'placesfollowup':
        res = call_api2(req)
    elif action == 'googlesearch':
        res = googleSearch(req)
    else :
        log.error('Unexpected action.')

    print('Action: ' + action)
    print(res)
    

    return make_response(jsonify(res))


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
