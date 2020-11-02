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
firebaseApp = firebase_admin.initialize_app(cred)

publicVenueFirebasePath = ('/venues_public')
privateVenueFirebasePath = ('/venues_private')
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

def createRandomEvent():
	eventTempName = "event-"+randomword(10)
	eventTempStart = (datetime.datetime.now()+datetime.timedelta(hours=random.randint(-5,3))) #.strftime("%Y-%m-%d %H:00:00")
	eventTempEnd = (eventTempStart+datetime.timedelta(hours=random.randint(1,5)))
	eventTempStartString = eventTempStart.strftime("%Y-%m-%d %H:00:00")
	eventTempEndString = eventTempEnd.strftime("%Y-%m-%d %H:00:00")

	event = {
		"eventName": eventTempName,
		"eventStart": eventTempStartString,
		"eventEnd": eventTempEndString
	}
	return event

def isUserInVenue(venue,user,searchRange):
	distance_geo=geodesic((venue.coordinates["latitude"],venue.coordinates["longitude"]), 
		(user.coordinates["latitude"],user.coordinates["longitude"])).km
	#distance_circle=great_circle((lat_q,long_q), (lat_u,long_u)).km
	#print('distance geodesic i: %d, lat: %f, long: %f,j: %d lat: %f, long: %f is: %f' % (i,lat_q,long_q,j,lat_u,long_u,distance_geo))
	#print('distance great circle i: %d,j: %d is: %f' % (i,j,distance_circle))
	if(distance_geo<=searchRange):
		venue.peopleTotal += 1
		if ((user.gender).lower() == "male"):
			venue.male += 1
		elif ((user.gender).lower() == "female"):
			venue.female += 1
		
		if((venue.male == 0) and (venue.female == 0)):
			venue.setRatio(0)
			# venue.ratio = 0
		elif((venue.male != 0) and (venue.female == 0)):
			venue.setRatio(0)
			# venue.ratio = 0
		elif((venue.male == 0) and (venue.female != 0)):
			venue.setRatio(venue.female)
			# venue.ratio = venue.female
		elif((venue.male != 0) and (venue.female != 0)):
			venue.setRatio(venue.female/venue.male)
			# venue.ratio = (venue.female/venue.male)
		# venue.ratio = round(venue.ratio, 1)
		# venue.avgAge = venue.avgAge + ((user.age - venue.avgAge)/venue.peopleTotal)
		venue.setAge(venue.avgAge + ((user.age - venue.avgAge)/venue.peopleTotal))
		# venue.avgAge = round(venue.avgAge, 1)
		venue.users.append(user.storeId)



# initialize Venue Object with data retrieved from yelp and google APIs
def initializeVenue(venue):
	name = venue["name"]
	location = venue["location"]["display_address"]
	coordinates = {
		"latitude": venue["coordinates"]["latitude"],
		"longitude": venue["coordinates"]["longitude"]
	}
	yelpId = venue["id"]
	website = venue["url"]
	pictureUrl = venue["image_url"]
	website = venue["url"]
	peopleTotal = 0
	male = 0
	female = 0
	ratio = 0
	rating = venue["rating"]
	avgAge = 0
	users = ["NULL"]
	if("price" in venue):
		print("price exist")
		price = venue["price"]
	else:
		print("price DON'T exist")
		return None
	
	categories = []

	for category in venue["categories"]:
		categories.append(category['title'])
	print('cateogies: ', categories)

	events = dict()
	activeEvent = {"NULL":"NULL"}

	for i in range(random.randint(2,10)):
		tmpEvent = createRandomEvent()
		# print(tmpEvent)
		events[tmpEvent['eventName']] = tmpEvent
	
	# print(events)

	googleVenue = gmaps.places(query=name,location=(coordinates["latitude"],coordinates["longitude"]))
	# print("GOOGLE VENUE RESULTS: ", googleVenue["results"][0])
	googleId = googleVenue["results"][0]["place_id"]
	if("opening_hours" in googleVenue["results"][0]):
		print("opening hours exist")
		openNow = True #googleVenue["results"][0]["opening_hours"]["open_now"]
	else:
		print("opening hours DONT exist")
		return None
		# openNow = False
	pt_response=populartimes.get_id(API_KEY, googleId)

	if("populartimes" in pt_response):
		pop_time_resp = pt_response["populartimes"]
		busyTimes = extract_times(pop_time_resp)
		# print("busy times for: " + name)
		# print(busyTimes)


		return Venue("NULL", googleId, yelpId, name, 
			location, coordinates, website, peopleTotal, 
			male, female, ratio, pictureUrl, rating, avgAge, openNow, 
			busyTimes, events, activeEvent, users, price, categories)
	else:
		return None


# get a bunch of random venues using YELP API
def getVenues(numReqQueries):
	totalVenues = []
	numQueries = numReqQueries
	for i in range(0,ceil(numReqQueries/50),1):
		if(numQueries > 50):

			venues = yelp_api.search_query(categories= 'bars,pubs', latitude=43.648360,longitude=-79.388940, radius=2000, limit=50, offset=(50*i))
			if(len(totalVenues) != 0):
				totalVenues.extend(venues["businesses"])
			else:
				totalVenues = venues["businesses"]
			numQueries = numQueries - 50
		else:
			venues = yelp_api.search_query(categories= 'bars,pubs', latitude=43.648360,longitude=-79.388940, radius=2000, limit=numQueries, offset=(50*i))
			if(len(totalVenues) != 0):
				totalVenues.extend(venues["businesses"])
			else:
				totalVenues = venues["businesses"]

	return totalVenues
	# venues = yelp_api.search_query(categories= 'bars,pubs', latitude=43.648360,longitude=-79.388940, radius=2000, limit=50, offset=0)
	# print(type(venues["businesses"]))
	# return venues["businesses"]

# update venue objects (update events, update peopleTotal, update male, update female, update ratio, update avgAge)
def updateVenues(venueList, userList):
	eventsToRemove = dict()
	for venue in venueList:
		venue.users = []
		# update people (check if 'user' is in the venue)
		# print("venue before adding users: ", vars(venue))
		for user in userList:
			uIn = isUserInVenue(venue,user,0.01)
			

		# print("venue after adding users: ", vars(venue))

		
		# update events
		# print("the events of " + venue.name + " BEFORE:")
		# print(venue.events)
		for e in venue.events:
			# print(e)
			# print("event START TIME: ", datetime.datetime.strptime(venue.events[e]["eventStart"], "%Y-%m-%d %H:00:00"))
			# print("event END TIME: ", datetime.datetime.strptime(venue.events[e]["eventEnd"], "%Y-%m-%d %H:00:00"))
			if(datetime.datetime.strptime(venue.events[e]["eventEnd"], "%Y-%m-%d %H:00:00") < datetime.datetime.now()):
				# print("event ENDED")
				# del venue.events[e]
				eventsToRemove[e]=venue.events[e]["eventName"]
			elif(datetime.datetime.strptime(venue.events[e]["eventStart"], "%Y-%m-%d %H:00:00") < datetime.datetime.now() 
					< datetime.datetime.strptime(venue.events[e]["eventEnd"], "%Y-%m-%d %H:00:00")):
				# print("event ONGOING")
				if("NULL" in venue.activeEvent):
					del venue.activeEvent["NULL"]
				venue.activeEvent[venue.events[e]["eventName"]]=venue.events[e]
			# else:
				# print("event hasn't happend yet!")
		# print("events to REMOVE: ")
		# print(eventsToRemove)

		for eToRm in eventsToRemove:
			if(eToRm in venue.events):
				del venue.events[eToRm]
		# print("the events of " + venue.name + " AFTER:")
		# print(venue.events)
		# print("the ACTIVE events of " + venue.name + " AFTER:")
		# print(venue.activeEvent)
		
# ********* FIREBASE FUNCTIONS START **************
def uploadVenuesToFirebase(venueList,fb_path):
	if(fb_path == privateVenueFirebasePath):
		print('private upload...')
		for venue in venueList:
			if(venue.storeId != "NULL"):
				print('private venue: ' + venue.name + ' exists. Executing a PUT')
				firebase.put(fb_path,"/"+venue.storeId, {k:v for k, v in vars(venue).items() if (k != 'storeId' and v != [] and v != {'NULL':'NULL'})})
			else:
				print('private venue: ' + venue.name + ' DOES NOT exist. Executing a PUSH')
				key = firebase.post(fb_path,{k:v for k, v in vars(venue).items() if (k != 'storeId' and v != [] and v != {'NULL':'NULL'})})
				venue.storeId = key['name']
	elif(fb_path == publicVenueFirebasePath):
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

def uploadUsersToFirebase(userList,fb_path):

	print('public USER upload...')
	for user in userList:
		key = firebase.post(fb_path,{k:v for k, v in vars(user).items() if k != 'storeId'})
		user.storeId = key['name']	

def syncVenuesWithFirebase(fb_path):
	Venues = VenuesClass()
	venuesJSON = firebase.get(fb_path,None)
	for venue in venuesJSON.keys():
		print("information for venue: " + venue)
		print(venuesJSON[venue])
		print("\n")
		busyTime = dict()
		j = 0
		for r in venuesJSON[venue]['busyTime']:
			busyTime[str(j)]= r
			j = j+1
		
		try:
			users = venuesJSON[venue]['users']
		except:
			users = ["NULL"]
		
		v = Venue(venue,venuesJSON[venue]['googleId'],venuesJSON[venue]['yelpId'],
		venuesJSON[venue]['name'],venuesJSON[venue]['location'],
		venuesJSON[venue]['coordinates'],venuesJSON[venue]['website'],
		venuesJSON[venue]['peopleTotal'],venuesJSON[venue]['male'], venuesJSON[venue]['female'],
		venuesJSON[venue]['ratio'],venuesJSON[venue]['pictureUrl'],
		venuesJSON[venue]['rating'],venuesJSON[venue]['avgAge'],
		venuesJSON[venue]['openNow'],busyTime, venuesJSON[venue]['events']
		, venuesJSON[venue]['activeEvent'], users, venuesJSON[venue]['price'], venuesJSON[venue]['categories'])
		Venues.appendVenue(v)
	return Venues

def syncUsersWithFirebase(fb_path):
	Users = UsersClass()
	usersJSON = firebase.get(fb_path,None)
	for user in usersJSON.keys():
		u = User(user, usersJSON[user]['age'], usersJSON[user]['gender'], usersJSON[user]['coordinates'], usersJSON[user]['uId'])
		Users.appendUser(u)
	return Users



# ********* FIREBASE FUNCTIONS END   **************

def initializeVenuesInFirebase(fb_path):
	Venues = VenuesClass()
	venues = getVenues(120)
	for venue in venues:
		Venue = initializeVenue(venue)
		if (Venue != None):
			print("venue added: ", Venue.name)
			Venues.appendVenue(Venue)
		else:
			print("venue not added!")
	uploadVenuesToFirebase(Venues.getAllVenues(), fb_path)
	return Venues

def initializeUsersInFirebase(Venues, fb_path):
	Users = UsersClass()
	# gender = ["Male","Female","Other"]
	gender = ["Male","Female"]
	for venue in Venues:

		uCoordinates = {
			"latitude": venue.coordinates["latitude"],
			"longitude": venue.coordinates["longitude"]
		}
		for i in range(random.randint(0,2)):
			uAge = random.randint(18,99)
			uGender = gender[random.randint(0,1)]
			u = User("NULL", uAge, uGender, uCoordinates, randomword(10))
			Users.appendUser(u)
	Users.printAllUser()
	uploadUsersToFirebase(Users.getAllUsers(),fb_path)



	return Users

def main():
	print("Starting firebase manager...")
	
	if(1 == 1):
		#run this to initialize venues and post them to FB ****************************************************************
		Venues = initializeVenuesInFirebase(privateVenueFirebasePath)
		# Venues.printAllVenues()

		# *****************************************************************************************************************
		
	if(1 == 1):	
		#run this to initialize users based on venues location and post them to FB ****************************************
		Users = initializeUsersInFirebase(Venues.getAllVenues(), publicUserFirebasePath)

		# *****************************************************************************************************************

	if(1 == 0):
		#run this if firebase ALREADY has venues and you want to get a local copy *****************************************
		Venues = syncVenuesWithFirebase(privateVenueFirebasePath)
		# Venues.printAllVenues()

		#upload private version of venues to public (simplified and less data version)
		uploadVenuesToFirebase(Venues.getAllVenues(), publicVenueFirebasePath)
		# Venues.printAllVenues()
		
		# *****************************************************************************************************************
		
		
	if(1 == 0):
		#run this if firebase ALREADY has users and you want to get a local copy *****************************************
		Users = syncUsersWithFirebase(publicUserFirebasePath)
		# Users.printAllUser()

		# *****************************************************************************************************************
	
	if(1 == 1):
		#run this to UPDATE the Venues (REQUIRED: Venues (generated or from FB) and Users (generated or from FB)) *********
		updateVenues(Venues.getAllVenues(), Users.getAllUsers())
		# Venues.printAllVenues()

		uploadVenuesToFirebase(Venues.getAllVenues(), privateVenueFirebasePath)
		uploadVenuesToFirebase(Venues.getAllVenues(), publicVenueFirebasePath)
		# *****************************************************************************************************************


	# if(0 == 1):
	# 	#run this to test randomEvent generation **************************************************************************
	# 	events = dict()
	# 	for i in range(5):
	# 		tmpEvent = createRandomEvent()
	# 		print(tmpEvent)
	# 		events[tmpEvent['eventName']] = tmpEvent
	# 	print(events)
	# 	# *****************************************************************************************************************

if __name__ == "__main__":
	main()