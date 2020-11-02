from firebase import firebase
from yelpapi import YelpAPI
from pprint import pprint
import json
from math import radians, cos, sin, asin, sqrt, ceil
from pygeocoder import Geocoder
from geopy.geocoders import GoogleV3
from geopy.distance import geodesic
from geopy.distance import great_circle
# from random import randint
import random
import string
import time
import datetime
import copy

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import db

from icalendar import Calendar, Event
from icalevents import icalevents
from datetime import date, timedelta, datetime
from pytz import timezone
import pytz

import googlemaps
import populartimes
#from GoogleMapsAPIKey import get_my_key
#REFERENCE: https://googlemaps.github.io/google-maps-services-python/docs/
API_KEY = "AIzaSyDGFE76yB56RcMHDa-tMESJjx3Ukeiy70Y"
gmaps = googlemaps.Client(key = API_KEY)
api_key='8auFVhR1WTiqecfzntGHWEMDMHRpkvSZfIR17sNFImRok0yz22MAHyULEHpktxl-6yLHYBkB4zVETSQrk32YQd9aJBNRdL_N3LQ_RuE2f6Ac31LoP16rGtYJVCSZW3Yx'
yelp_api = YelpAPI(api_key)
firebase = firebase.FirebaseApplication('https://fir-project0-f4e17.firebaseio.com/', None)

# FIREBASE ADMIN INITIALIZE
cred = credentials.Certificate('./ServiceAccountKey.json')
firebaseApp = firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://fir-project0-f4e17.firebaseio.com/'
})

# publicVenueFirebasePath = ('/venues_public')
# privateVenueFirebasePath = ('/venues_private')

publicVenueFirebasePath = ('/venues_public_test')
privateVenueFirebasePath = ('/venues_private_test')
# publicVenueFirebasePathTest = ('/venues_public_test')
# privateVenueFirebasePathTest = ('/venues_private_test')

# publicUserFirebasePath = ('/users_v1')
publicUserFirebasePath = ('/users_public')
# oldVenuesFirebasePath = ('/g_api_venues')

class User:
	def __init__(self, storeId, age, gender, coordinates, uId):
		self.storeId = storeId
		self.age = age
		self.gender = gender
		self.coordinates = coordinates
		self.uId = uId
	
class UsersClass:
	def __init__(self):
		self.users = []
	def appendUser(self, User):
		self.users.append(User)
	def printAllUser(self):
		print("Printing All User: \n")
		for user in self.users:
			print(vars(user))
	def getAllUsers(self):
		return self.users


class Venue:
	def __init__(self, storeId, googleId, 
				yelpId, name, location, 
				coordinates, website, peopleTotal, 
				male, female,
				ratio, pictureUrl, rating, 
				avgAge, openNow, busyTime, 
				events, activeEvent, users, price,
				categories):
		self.storeId = storeId
		self.googleId = googleId
		self.yelpId = yelpId
		self.name = name
		self.coordinates = coordinates
		self.location = location
		self.website = website
		self.peopleTotal = peopleTotal
		self.male = male
		self.female = female
		self.ratio = round(ratio,1) #PRIVATE
		self.pictureUrl = pictureUrl
		self.rating = round(rating, 1) #PRIVATE
		self.avgAge = round(avgAge,1)	#PRIVATE
		self.openNow = openNow
		self.busyTime = busyTime
		self.events = events
		self.activeEvent = activeEvent
		self.users = users
		self.price = price
		self.categories = categories
	def setAge(self,avgAge):
		self.avgAge = round(avgAge,1)
	def setRating(self,rating):
		self.rating = round(rating,1)
	def setRatio(self,ratio):
		self.ratio = round(ratio,1)

class VenuesClass:
	def __init__(self):
		self.venues = []
	def appendVenue(self, Venue):
		self.venues.append(Venue)
	def printAllVenues(self):
		print("Printing All Venues: \n")
		for venue in self.venues:
			print(vars(venue))
	def getAllVenues(self):
		return self.venues

# helper functions		
def extract_times(pop_time_resp):


	times = dict()
	j = 0
	for i in range(len(pop_time_resp)):
		
		for k in range(len(pop_time_resp[i]['data'])):
			#times={[str(j)]: str(pop_time_resp[i]['data'][k])}
			if str(j) in times:
				times[str(j)].append(pop_time_resp[i]['data'][k])
			#times[str(j)]=str(pop_time_resp[i]['data'][k])
			else:
				times[str(j)]=[pop_time_resp[i]['data'][k]]

		j=j+1
	return times
def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


# ********* FIREBASE FUNCTIONS START **************
def uploadVenuesToFirebase(venueList,fb_path):
	
    if(fb_path == privateVenueFirebasePath):
        # if(fb_path == privateVenueFirebasePathTest):
        print('private upload...')
        for venue in venueList:
            if(venue.storeId != "NULL"):
                # print('private venue: ' + venue.name + ' exists. Executing a PUT')
                firebase.put(fb_path,"/"+venue.storeId, {k:v for k, v in vars(venue).items() if (k != 'storeId' and v != [] and v != {'NULL':'NULL'})}) #TO DO MAYBE? don't add if v == 'NULL'
                # for k,v in vars(venue).items():
                #     print("k: ")
                #     print(k)
                #     print("v: ")
                #     print(v)
            else:
                # print('private venue: ' + venue.name + ' DOES NOT exist. Executing a PUSH')
                key = firebase.post(fb_path,{k:v for k, v in vars(venue).items() if (k != 'storeId' and v != [] and v != {'NULL':'NULL'})})
                print('store id: ', key['name'])
                venue.storeId = key['name']
                # for k,v in vars(venue).items():
                #     print("k: ")
                #     print(k)
                #     print("v: ")
                #     print(v)

    elif(fb_path == publicVenueFirebasePath):
        # elif(fb_path == publicVenueFirebasePathTest):
        print('public upload...')
        hour = datetime.datetime.now().hour
        weekDay = datetime.datetime.today().weekday()
        for venue in venueList:
            publicVenue = copy.deepcopy(venue)
            publicVenue.busyTime = venue.busyTime[str(weekDay)][hour]
            publicVenue = {k:v for k, v in vars(publicVenue).items() if (k != 'storeId' and k != 'events' and k != 'users' and v != [] and v != {'NULL':'NULL'})}
            # PUT and provide the key that is the same as the one in the private database
            key = firebase.put(fb_path,"/"+venue.storeId, publicVenue)
            # venue.storeId = key['name'] # don't update the key, this should remain the same

    else:
        print('please give a valid path!')

def getVenueStoreIdFromgGoogleId(googleId):
    print("here")
    dbUrl = 'venues_private/'
    ref = db.reference(dbUrl)
    snapshot = ref.order_by_child('googleId').equal_to(googleId).get()
    for key in snapshot:
        print(key)
    return key
def storeEventFirebase(storeId, name, start, end):
    dbUrl = 'venues_private/'+storeId+'/events'
    ref = db.reference(dbUrl)
    ref.push({
        'eventName':name,
        'eventStart': start,
        'eventEnd': end
    })
def addEventToVenue(venueName,venueAddress,eventName,eventStart,eventEnd):
    gVenueData = gmaps.places(query=venueName, location=venueAddress)
    googleId = gVenueData['results'][0]["place_id"]
    venueStoreId = getVenueStoreIdFromgGoogleId(googleId)
    print("store id: ", venueStoreId)
    storeEventFirebase(venueStoreId, eventName, eventStart, eventEnd)

def getYelpApiData(venueName, venueAddress):
    yVenueData = yelp_api.business_match_query(name=venueName,
                                         address1=venueAddress[0],
                                         city=venueAddress[1],
                                         state='ON',
                                         country='CA')
    # print(yVenueData)
    print(yVenueData['businesses'][0]['id'])
    yVenueData = yelp_api.business_query(id=yVenueData['businesses'][0]['id'])
    categories = []
    for category in yVenueData['categories']:
        categories.append(category['title'])
    yVenueDataFormatted = {
        # 'googleId': gVenueData['results'][0]["place_id"],
        # 'coordinates': {
        #     'latitude': gVenueData["results"][0]["geometry"]["location"]["lat"],
        #     'longitude': gVenueData["results"][0]["geometry"]["location"]["lng"]
        # },
        # 'location': gVenueData['results'][0]['formatted_address'].split(','),
        'name': yVenueData['name'],
        # 'rating': gVenueData['results'][0]['rating'],
        'price':yVenueData['price'],
        # 'website':"",
        # 'categories':yVenueData['categories'],
        'categories':categories,
        'yelpId':yVenueData['id'],
        'pictureUrl': yVenueData['image_url']
    }  
    return yVenueDataFormatted 

def getGoogleApiData(venueName, venueAddress):
    gVenueData = gmaps.places(query=venueName, location=venueAddress)
    gVenueDataFormatted = {
        'googleId': gVenueData['results'][0]["place_id"],
        'coordinates': {
            'latitude': gVenueData["results"][0]["geometry"]["location"]["lat"],
            'longitude': gVenueData["results"][0]["geometry"]["location"]["lng"]
        },
        'location': gVenueData['results'][0]['formatted_address'].split(','),
        # 'name': gVenueData['results'][0]['name'],
        'rating': gVenueData['results'][0]['rating'],
        # 'price':"",
        'website':"",
        # 'categories':"",
        # 'yelpId':""
    }
    gVenueData = gmaps.place(place_id=gVenueDataFormatted['googleId'], fields=['website'])
    gVenueDataFormatted['website']=gVenueData["result"]["website"]
    # print("\n")
    # print(gVenueDataFormatted)
    return gVenueDataFormatted
def addVenueToFirebase(venueName, venueAddress):
    print('hello')
    gVenueDataFormatted = getGoogleApiData(venueName, venueAddress)
    yVenueDataFormatted = getYelpApiData(venueName, gVenueDataFormatted['location'])
    venuePopularTimes = populartimes.get_id(API_KEY, gVenueDataFormatted['googleId'])

    if("populartimes" in venuePopularTimes):
        pop_time_resp = venuePopularTimes["populartimes"]
        busyTimes = extract_times(pop_time_resp)
    
    Venues = VenuesClass()
	# venues = getVenues(170)
	# for venue in venues:
	# 	Venue = initializeVenue(venue)
	# 	if (Venue != None):
	# 		print("venue added: ", Venue.name)
	# 		Venues.appendVenue(Venue)
	# 	else:
	# 		print("venue not added!")
    venue = Venue (
        "NULL",
        gVenueDataFormatted['googleId'],
        yVenueDataFormatted['yelpId'],
        yVenueDataFormatted['name'],
        gVenueDataFormatted['location'],
        gVenueDataFormatted['coordinates'],
        gVenueDataFormatted['website'],
        0,
        0,
        0,
        0,
        yVenueDataFormatted['pictureUrl'],
        gVenueDataFormatted['rating'],
        0,
        True,
        busyTimes,
        [],
        {"NULL":"NULL"},
        [],
        yVenueDataFormatted['price'],
        yVenueDataFormatted['categories']
    )
    # print(vars(venue))

    Venues.appendVenue(venue)
#     publicVenueFirebasePathTest = ('/venues_public_test')
# privateVenueFirebasePathTest = ('/venues_private_test')
    uploadVenuesToFirebase(Venues.getAllVenues(),privateVenueFirebasePath)
    uploadVenuesToFirebase(Venues.getAllVenues(),publicVenueFirebasePath)

def readVenuesFromFile(file):
    with open(file) as f:
        jsonVenues = json.load(f)

    print(jsonVenues)
    for venue in jsonVenues['venues']:
        print(venue)
        addVenueToFirebase(venue['name'],venue['location'])




    return

def parseEvents(icsFile):
    start = date(2020,11,2)
    end = date(2020,11,9)
    evs = icalevents.events(url=None, file = icsFile, start = start, end = end)
    
    for events in evs:
        start = events.start
        end = events.end

        localStart = start.astimezone(pytz.timezone('America/Toronto'))
        localEnd = end.astimezone(pytz.timezone('America/Toronto'))

        localStartString = localStart.strftime("%Y-%m-%d %H:%M:%S")
        localEndString = localEnd.strftime("%Y-%m-%d %H:%M:%S")
        title = events.summary.split(':')
        venueName = title[0].strip()
        eventName = title[1].strip()
        venueAddress = (events.location).replace('\n',' ')
        # print(venueName)
        # print(eventName)
        # print(venueAddress)
        addEventToVenue(venueName, venueAddress, eventName, localStartString, localEndString)
def main():
    if(1==0):
        readVenuesFromFile('venues.json')
    if(1==1):
        parseEvents('TestICS.ics')
    if(1 == 0):
        addVenueToFirebase("Turtle Jack's Yonge", "11740 Yonge St, Richmond Hill, ON L4E 0K4")
    if(1 == 0):
        # addEventToVenue("Patria", "478 King St W, Toronto, ON M5V 1L7",eventName="testEvent",eventStart="2020-10-27 11:00:00",eventEnd="2020-10-27 14:00:00")
        # addEventToVenue("Patria", "478 King St W, Toronto, ON M5V 1L7",eventName="testEvent",eventStart="2020-10-27 14:00:00",eventEnd="2020-10-27 15:00:00")
        addEventToVenue("Turtle Jack's Yonge", "11740 Yonge St, Richmond Hill, ON L4E 0K4",eventName="test1",eventStart="2020-10-28 12:00:00",eventEnd="2020-10-28 14:10:00")
        # addEventToVenue("Turtle Jack's Yonge", "11740 Yonge St, Richmond Hill, ON L4E 0K4",eventName="testEvent",eventStart="2020-10-27 13:00:00",eventEnd="2020-10-27 16:10:00")
        # addEventToVenue("Grossman's Tavern", "379 Spadina Ave, Toronto, ON M5T 2G3",eventName="testEvent",eventStart="2020-10-27 13:00:00",eventEnd="2020-10-27 16:10:00")
        addEventToVenue("Wvrst", "609 King Street W, Toronto, ON M5V 1M5",eventName="test2",eventStart="2020-10-28 13:00:00",eventEnd="2020-10-28 15:10:00")

if __name__ == "__main__":
	main()