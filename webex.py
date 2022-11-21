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

from webexteamssdk import WebexTeamsAPI
from urllib.parse import urljoin

from dotenv import load_dotenv
import os
import json
import base64


# load all environment variables
load_dotenv()

# Create the Webex Teams API connection object
api = WebexTeamsAPI(access_token=os.environ['WEBEX_TEAMS_ACCESS_TOKEN'])
WEBEX_TEAMS_BOT_NAME = os.environ['WEBEX_TEAMS_BOT_NAME'] 

WEBHOOK_NAME = "Help Button Bot"
CARDS_WEBHOOK_RESOURCE = "attachmentActions"
CARDS_WEBHOOK_EVENT = "created"
# Target url suffix for Webhook = target when button on card is pressed
WEBHOOK_URL_SUFFIX = "/webhookEvent"
# External webhook base url 
EXTERNAL_WEBHOOK_URL = os.environ['EXTERNAL_WEBHOOK_URL']

# List of employees to receive a notfication on help request
NOTIFICATION_RECEIVER = json.loads(os.environ['NOTIFICATION_RECEIVER'])
BOTROOM_TITLE = 'In-Store Help Bot'
#Card message content for notification
NOTIFY_CARD_JSON = "notifyCard.json"
#card message content for accepted request
ACCEPT_CARD_JSON = "acceptedCard.json"
#Message details for notification card
messageDetailsNotifyRequest = ""
#Message details for accepter card
messageDetailsAcceptedRequest = ""

##  Helper methods
#Save content of seperate JSON file in variable
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())

		f.close()

	return json_content


#Converstions of jpg image to base64 string to prevent the need to host the image publically and thereby make it accessible in the webex teams card message
def createDataURI(image_path):

    print('Convert map image to data URI')
    
    with open(image_path, "rb") as img_file:
        base64image = base64.b64encode(img_file.read()).decode('utf-8')        
        return 'data:image/png;base64,{}'.format(base64image)


# Find all rooms that have a specific title
def getDemoRooms():

    global BOTROOM_TITLE

    all_rooms = api.rooms.list()
    demo_rooms = [room for room in all_rooms if BOTROOM_TITLE in room.title]

    return demo_rooms


#Identifiy card type based on the messageID that was saved when messages was created in the backend
def identifyCardType(messageID):

    global messageDetailsNotifyRequest, messageDetailsAcceptedRequest

    if messageID == messageDetailsNotifyRequest.id:
        return 'noftifyAll'

    elif messageID == messageDetailsAcceptedRequest.id:
        return 'accepted'
        

##  Message methods
# Delete all demo rooms and remove the message details
def cleanUpRoomAndMessages():

    global messageDetailsNotifyRequest, messageDetailsAcceptedRequest
    
    messageDetailsNotifyRequest = ""
    messageDetailsAcceptedRequest=""
    
    demo_rooms = getDemoRooms()

    for room in demo_rooms:
        api.rooms.delete(room.id)


# Delete all employees from the Bot room that didn't accept the request
def removeOtherEmployeesFromRoom(notificationAccepterPersonId):

    demo_rooms = getDemoRooms()
    
    for room in demo_rooms:
        members = api.memberships.list(room.id)
        for member in members:

            if member.personId != notificationAccepterPersonId and member.personDisplayName != WEBEX_TEAMS_BOT_NAME:
                api.memberships.delete(member.id)
                print("Deleted the following employee from the Bot room:", member.personDisplayName)


#Notfiy request accepter that he accepted - share accepter message in Bot room
def notifyAccepter():
    
    global messageDetailsNotifyRequest, messageDetailsAcceptedRequest, ACCEPT_CARD_JSON
    
    demo_rooms = getDemoRooms()

    for room in demo_rooms:  
        
        messageDetailsAcceptedRequest = api.messages.create(room.id, text="If you see this your client cannot render cards", attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": getJson(ACCEPT_CARD_JSON)
            }])
        api.messages.delete(messageDetailsNotifyRequest.id)


#Notfiy all specified employees that new help request is available
def notifyEmployees():

    global messageDetailsNotifyRequest, NOTIFY_CARD_JSON, NOTIFICATION_RECEIVER, BOTROOM_TITLE
    print("before cleanup")
    cleanUpRoomAndMessages()
    print("after cleanup")
    demo_room = api.rooms.create(BOTROOM_TITLE)
    print("demorooms", demo_room)
    print("notification receiver", NOTIFICATION_RECEIVER)
    # Add employees specified to the new Bot room
    for email in NOTIFICATION_RECEIVER:
        print("email", email)
        api.memberships.create(demo_room.id, personEmail=email)
    print("before message")
    # Post a message to the new room, and upload a file
    messageDetailsNotifyRequest = api.messages.create(demo_room.id, text="If you see this your client cannot render cards.", attachments=[{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": getJson(NOTIFY_CARD_JSON)
        }])

## Webhook methods
#Delete webhooks created by this script
def deleteWebhooksWithName():

    global WEBHOOK_NAME
    
    for webhook in api.webhooks.list():
        if webhook.name == WEBHOOK_NAME:
            print("Deleting Webhook:", webhook.name, webhook.targetUrl)
            api.webhooks.delete(webhook.id)


#Create the Webex Teams webhooks we need for our bot
def createWebhooks():

    global CARDS_WEBHOOK_RESOURCE, CARDS_WEBHOOK_EVENT, WEBHOOK_NAME, EXTERNAL_WEBHOOK_URL, WEBHOOK_URL_SUFFIX 

    print("Creating Attachment Actions Webhook...")

    webhook = api.webhooks.create(
        resource=CARDS_WEBHOOK_RESOURCE,
        event=CARDS_WEBHOOK_EVENT,
        name=WEBHOOK_NAME,
        targetUrl=urljoin(EXTERNAL_WEBHOOK_URL, WEBHOOK_URL_SUFFIX)
    )

    print("Webhook successfully created.", webhook.name, webhook.targetUrl)
