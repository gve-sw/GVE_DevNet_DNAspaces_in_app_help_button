""" Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

# Import Section
from flask import Flask, render_template, request, redirect, url_for
import requests
import json
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw
from webexteamssdk import WebexTeamsAPI, Webhook
from pprint import pprint

from webex import notifyEmployees, createWebhooks, deleteWebhooksWithName, cleanUpRoomAndMessages, removeOtherEmployeesFromRoom, notifyAccepter, identifyCardType, CARDS_WEBHOOK_RESOURCE, CARDS_WEBHOOK_EVENT, NOTIFY_CARD_JSON, ACCEPT_CARD_JSON, createDataURI


# load all environment variables
load_dotenv()

#Global variables
app = Flask(__name__)

# DNA Spaces Location cloud API base url
BASE_URL = os.environ['BASE_URL']
#DNA Spaces Bearer token
BEARER = os.environ['BEARER']

#Mac address of customer, that simulates a customer in a store with a specific location  
CLIENTMAC = os.environ['CLIENTMAC']
#Name of map image available in DNA Spaces, in which the customer is located
MAPIMAGENAME = os.environ['MAPIMAGE']
#Floor ID of the floor associated with the DNA Spaces map, in which the customer is located
FLOORID = os.environ['FLOORID']

#Filename of map image of floor, in which customer is located
MAPIMAGE = "map.jpg"
#Filename of map image with highlighted customer position
MAPIMAGEWITHCLIENT = "mapannotate.jpg"


#Execute GET request with given endpoint url and querystring
def get(endpoint, querystring):
    global BASE_URL, BEARER

    request_url = "{}/{}".format(BASE_URL, endpoint)    
    headers = {'Authorization': 'Bearer' ' {}'.format(BEARER) }
 
    response = requests.get(request_url, headers=headers, params=querystring)
    
    if response.status_code != 200:
        print(request_url)
        print('An error happend: Code:')
        print(response.status_code)  

    return response


#Retrieve map image via DNA Spaces API and save it as map.jpg
def retrieveAndSaveMap():
    
    global MAPIMAGENAME, MAPIMAGE

    map = get("map/images/floor/"+ MAPIMAGENAME , {})
    
    if map.status_code == 200:
        with open(MAPIMAGE, 'wb') as f:
            f.write(map.content)

    print('Retrieved map via DNA Spaces API and saved it as:', MAPIMAGE)

    return MAPIMAGE


# Retrieve and return map information like size map size in px and ft via DNA Spaces API 
def getMapSizes(FLOORID):     
    
    mapinformation = get("map/elements/"+ FLOORID , {}).json()
    print('Retrieved map information via DNA Spaces API') 

    widthpx = mapinformation['map']['details']['image']['width']
    heightpx = mapinformation['map']['details']['image']['height']
    print('Read map size in px from response json. Map size(width, height):', widthpx, heightpx)

    widthft = mapinformation['map']['details']['width']
    heightft = mapinformation['map']['details']['length']  
    print('Read map size in ft from response json. Map size in ft (width, heigth): ', widthft, heightft)

    return widthpx, heightpx, widthft, heightft


#Retrieve information about a specific client based on the MAC address and calculate x and y coordinate of the client location on the associated map 
def getClientCoordinates(CLIENTMAC, widthpx, heightpx, widthft, heightft):
    
    client = get("clients", {'deviceId': CLIENTMAC}).json() #Info: use query parameter "ssid" to filter based on the SSID (Available for associated clients only.); To check if client is currently connected to network use the "associated" field in the json response (here client variable)
    print('Retrieved information about client with MAC address', CLIENTMAC ,'via DNA Spaces API')   
    
    xft = client['results'][0]['coordinates'][0]
    yft = client['results'][0]['coordinates'][1]
    print('Read coordinates of client from client response json in ft. Client coordinates in ft (x, y): ', xft, yft)
     
    x = (widthpx/widthft)*(xft)
    y = (heightpx/heightft)*(yft)
    print('Calculated postion of client on map in px, based on map size in ft and px and client coordinates in ft. Client coordinate in px (x,y):', x,y)

    return x, y


def drawClientPositionOnMap(x,y):

    global MAPIMAGE, MAPIMAGEWITHCLIENT

    with Image.open(MAPIMAGE) as im:

        draw = ImageDraw.Draw(im)
        draw.ellipse((x-5, y-5, x+5, y+5), fill = 'red', outline ='red')

        # write to stdout
        im.save(MAPIMAGEWITHCLIENT)
    
    print('Did draw client position on map and saved as:', MAPIMAGEWITHCLIENT)


#Add annotated map to webex card message json for employee notification message
def addAnnotatedMapToCardJson():

    global NOTIFY_CARD_JSON, ACCEPT_CARD_JSON, MAPIMAGEWITHCLIENT

    cardsToChange = [NOTIFY_CARD_JSON, ACCEPT_CARD_JSON]

    for filename in cardsToChange:
        
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)

        for elem in data['body']:
            if elem['type'] == 'Image':
                elem['url'] = createDataURI(MAPIMAGEWITHCLIENT)

        with open(filename, "w") as jsonFile:
            json.dump(data, jsonFile)

    print('Added annotated map to webex card json for employee notification message')


#Routes
@app.route('/', methods=["GET","POST"])
def index():
    try:
        cleanUpRoomAndMessages()

        return render_template('home.html', error=False)

    except Exception as e: 
        print("Error Home:", e)   
        return render_template('home.html', error=True) 


@app.route('/helpRequest', methods=["GET","POST"])
def helpRequest():
    try:
        global MAPIMAGENAME, FLOORID, CLIENTMAC
        #Clean up - remove old files:
        if (os.path.exists(MAPIMAGE) and os.path.exists(MAPIMAGEWITHCLIENT)):
            os.remove(MAPIMAGE)
            os.remove(MAPIMAGEWITHCLIENT)
        
        #Retrieve map image via DNA Spaces API
        retrieveAndSaveMap()

        #Retrieve map size via DNA Spaces API
        widthpx, heightpx, widthft, heightft = getMapSizes(FLOORID)

        #Retrieve customer location coordinates via DNA Spaces API and calculate client position in px
        clientx, clienty = getClientCoordinates(CLIENTMAC, widthpx, heightpx, widthft, heightft)

        #Draw customer position on retrieved map
        drawClientPositionOnMap(clientx,clienty)
        
        #Add annotated map to notification card message content
        addAnnotatedMapToCardJson()

        #Send created message content to list of employees
        notifyEmployees()

        return render_template('helpRequested.html')

    except Exception as e: 
        print("Error Feedback:", e)  
        return render_template('helpRequested.html', error=True)


@app.route("/webhookEvent", methods=["GET","POST"])
def webhookEvent():
    
    print("Webhook event happend")
    
    webhook_obj = Webhook(request.json)
    
    # Handle an Action.Submit button press event
    if (webhook_obj.resource == CARDS_WEBHOOK_RESOURCE and webhook_obj.event == CARDS_WEBHOOK_EVENT):

        cardType = identifyCardType(webhook_obj.data.messageId)
        accepter = webhook_obj.data.personId
        print("Card type employee reacted to:", cardType)
        
        if cardType == 'noftifyAll':
            removeOtherEmployeesFromRoom(accepter)
            notifyAccepter()  

        elif cardType == 'accepted':
            cleanUpRoomAndMessages()
    else:
        print("IGNORING UNEXPECTED WEBHOOK:",webhook_obj)

    return "OK"

#Main Function
if __name__ == "__main__":
    
    # Delete preexisting webhooks created by this script
    deleteWebhooksWithName()
    cleanUpRoomAndMessages()

    createWebhooks()

    port = int(os.environ.get("PORT", 8000))
    try:
        # Start the Flask web server
        app.run(host="0.0.0.0", port=port)

    finally:
        print("Cleaning up webhooks...")
        deleteWebhooksWithName()
        cleanUpRoomAndMessages()

    


