from firebase import firebase
from yelpapi import YelpAPI
from pprint import pprint
import json
from math import radians, cos, sin, asin, sqrt
from pygeocoder import Geocoder
from geopy.geocoders import GoogleV3
from geopy.distance import geodesic
from geopy.distance import great_circle
from random import randint
import time
import datetime

import googlemaps
import populartimes
#from GoogleMapsAPIKey import get_my_key
#REFERENCE: https://googlemaps.github.io/google-maps-services-python/docs/
API_KEY = "AIzaSyDGFE76yB56RcMHDa-tMESJjx3Ukeiy70Y"

gmaps = googlemaps.Client(key = API_KEY)


class User:
	def __init__(self,key,lat,long,age):
		self.key=key
		self.lat=lat
		self.long=long
		self.age = age

class Query:
	def __init__(self,key,name,lat,long,times,people,avg_age):
		self.key=key
		self.name=name
		self.lat=lat
		self.long=long
		self.ppl=people
		self.ages=[]
		self.avg_age=avg_age
		self.populartimes=times
	def add_one_person(self):
		self.ppl = self.ppl+1
	def add_people(self,people):
		self.ppl=self.ppl+people
	def set_people(self,people):
		self.ppl=people
	def set_avg_age(self,age):
		self.avg_age=age
	def add_age(self,age):
		self.ages.append(age)
		print(self.ages)
	def assignPopularTimes(self,times):
		self.populartimes=times
	def average_age(self):
		if(self.ppl==0):
			self.avg_age = 0
			return
		print('number of ppl:',self.ppl)
		print('number of ages elements:',len(self.ages))
		for i in (self.ages):
			print('ages ',i)
			self.avg_age=self.avg_age+i
		self.avg_age = self.avg_age/self.ppl


def haversine(lon1, lat1, lon2, lat2):
	R = 6372.8

	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)

	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))

	return R * c

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
def store_query(search_results,initialize,fb_path):
	#store all query into /query database
	Queries=[]
	for i in range(len(search_results['businesses'])):
		query_name=search_results['businesses'][i]['name']
		query_lat=search_results['businesses'][i]['coordinates']['latitude']
		query_long=search_results['businesses'][i]['coordinates']['longitude']
		#print(query_name,query_lat)
		places_result = gmaps.places(query=query_name,location=(query_lat,query_long))

		#print(places_result["results"][0]["name"]) #this is the place ID
		# import pdb
		# pdb.set_trace()
		#print(places_result)
		p_id = places_result["results"][0]["place_id"]

		query_open_now = places_result["results"][0]["opening_hours"]["open_now"] #SEE IF CURRENTLY OPEN
		# # print(p_id)
		# # place_result = gmaps.place(place_id=p_id)
		# # pprint.pprint(place_result)


		pt_response=populartimes.get_id(API_KEY, p_id)

		# #pprint.pprint(pt_response)
		pop_time_resp = pt_response["populartimes"]

		
		times = extract_times(pop_time_resp)

		# pprint.pprint(pop_time_resp)
		#Queries[i].assignPopularTimes(pop_time_resp)
		people=randint(0,50)
		avg_age=randint(18,55)
		data = {'name': query_name, 
		'latitude': query_lat,
		'longitude': query_long,
		'open': query_open_now,
		'popular_times': times,
		'people': people,
		'avg_age': avg_age,
		'google_id':p_id}
		key = firebase.post(fb_path,data)

		a=Query(key,query_name,query_lat,query_long,times,people,avg_age)
		Queries.append(a)
		# id_fire=firebase.post('/query/','')
		# print id_fire
		# firebase.put('/query/'+id_fire['name']+query_name,'/latitude', query_lat)
		# firebase.patch('/query/'+id_fire['name']+'/latitude', query_lat)
		# firebase.patch('/query/'+id_fire['name']+'/longitude', query_long)
	return Queries
def clear_branch(firebase,fb_path):
	result = firebase.delete(fb_path,None)
	print("result:",result)
def clear_users(firebase):
	result = firebase.delete('/new_users',None)
	print("result:",result)
def make_users(firebase,queries):
	j=10
	for i in range(len(queries)):
		lat_q=Queries[i].lat
		long_q=Queries[i].long
		name_q=Queries[i].name
		num_ppl = randint(2,10)
		for k in range(1,num_ppl):
			gender_int=randint(0, 2)
			age_u = randint(20,50)
			if(gender_int==0):
				gender="male"
			elif(gender_int==1):
				gender="female"
			else:
				gender="other"
			name_u = name_q+str(k)
			print("making users: k, name:",k,name_u)
			#data = {'name':name_u,'age': age_u,'gender': gender,'latitude': lat_q,'longitude': long_q}
			data = {'name':name_u,'age': age_u,'gender': gender,'location':""}
			key = firebase.post("/new_users",data)
			location_data={'latitude': lat_q,'longitude': long_q}
			firebase.put('/new_users/'+key['name'],'/location', location_data)
						# id_fire=firebase.post('/query/','')
		# print id_fire
		# firebase.put('/query/'+id_fire['name']+query_name,'/latitude', query_lat)
		# firebase.patch('/query/'+id_fire['name']+'/latitude', query_lat)
		# firebase.patch('/query/'+id_fire['name']+'/longitude', query_long)

def create_venue(firebase,name,latitude,longitude,fb_path): #given a physical street address, make this into a VENUE in the firebase at the fb_path location
	
	data = {'name': name, 
		'latitude': latitude,
		'longitude': longitude,
		'people':0,
		'male':0,
		'female':0,
		'avg_age':25}
	key = firebase.post(fb_path,data)
	venue=Query(key,name,latitude,longitude)
	return venue
	# Queries.append(a)
def clear_venues_people(Venues):
	for ven in Venues:
		ven.set_people(0)
		ven.set_avg_age(0)

def getBusyMax(firebase,fb_path):
	result= firebase.get(fb_path,None)
	num_query = len(result)
	json_object = json.dumps(result)
	data = json.loads(json_object)
	week_day = datetime.datetime.today().weekday()
	hour= datetime.datetime.now().hour
	currMax = 0
	for v in data.values():
		# name= v['name']
		if type(v) != dict:
			continue
		else:
			busyFactor = int(v['popular_times'][week_day][hour])
			if(busyFactor > currMax):
				currMax=busyFactor
		# try:
		# 	busyFactor = int(v['popular_times'][week_day][hour])
		# 	# print("busyFactor for " + name + " " + str(busyFactor))
		# 	if(busyFactor > currMax):
		# 		currMax=busyFactor
		# except ValueError:
		# 	print("decoding issue with: ")
		# 	print(v)
	return currMax
def setBusyMax(firebase,fb_path,maxBusy):
	firebase.put(fb_path,'/currentMax',maxBusy)
def get_users(firebase,fb_path):
	#result = firebase.get('/places',None)
	#FOR OLD TEST /new_users is the path
	#FOR NEW TEST /users_v1 is the path
	result = firebase.get(fb_path,None)
	num_query = len(result)
	Users=[]
	print("total number of PEOPLE",num_query)
	print('\n')
	# print(result)
	# print(result[0])

	json_object = json.dumps(result)
	data = json.loads(json_object)
	i=1
	for v in data.values():
		age = int(v['age'])
		a=User(i,v['location']['latitude'], v['location']['longitude'],age)
		i=i+1
		Users.append(a)
	return Users
		#print(v['latitude'], v['longitude'])
	#json_object = json.dumps(result)
	#a = json.loads(json_object)
	#pprint(a)
def modify_queries(Queries,firebase):
	for i in range(len(Queries)):
		ppl = randint(1,50)
		avg_age = randint(20,40)
		#print(Queries[i].key['name'])
		firebase.put('/new_query/'+Queries[i].key['name'],'/people', ppl)
		firebase.put('/new_query/'+Queries[i].key['name'],'/avg_age', avg_age)
def upload_people(Queries,firebase,fb_path):
	for i in range(len(Queries)):
		#print(Queries[i].key['name'])
		#***************THIS IS THE OLD HARD CODED*****************
		#firebase.put('/new_query/'+Queries[i].key['name'],'/people', Queries[i].ppl)
		#firebase.put('/new_query/'+Queries[i].key['name'],'/avg_age', Queries[i].avg_age)
		firebase.put(fb_path+Queries[i].key['name'],'/people', Queries[i].ppl)
		firebase.put(fb_path+Queries[i].key['name'],'/avg_age', Queries[i].avg_age)

def upload_popular_time(Queries,firebase,fb_path):
	for i in range(len(Queries)):
		#firebase.put(fb_path+Queries[i].key['name'],'/popular_times',Queries[i].populartimes)
		day_of_week = 0
		for j in range(len(Queries[i].populartimes)):
			#print(Queries[i].populartimes[j]['name'])
			firebase.put(fb_path+Queries[i].key['name'],'/popular_times/'+str(day_of_week),Queries[i].populartimes[j]['name'])
			
			time = 0
			for k in range(len(Queries[i].populartimes[j]['data'])):
				firebase.put(fb_path+Queries[i].key['name'],'/popular_times/'+str(day_of_week)+"/"+str(time),Queries[i].populartimes[j]['data'][k])
				time = time+1
			day_of_week=day_of_week+1

				# print(Queries[i].populartimes[j]['data'][k])
def get_popular_time(Queries,firebase):
	for i in range(len(Queries)):
		q_name = Queries[i].name
		print(q_name)
		q_lat = Queries[i].lat
		#print(q_lat)
		q_long = Queries[i].long
		#print(q_long)

		places_result = gmaps.places(query=q_name,location=(q_lat,q_long))

		#print(places_result["results"][0]["name"]) #this is the place ID

		p_id = places_result["results"][0]["place_id"]
		# # print(p_id)
		# # place_result = gmaps.place(place_id=p_id)
		# # pprint.pprint(place_result)


		pt_response=populartimes.get_id(API_KEY, p_id)

		# #pprint.pprint(pt_response)
		pop_time_resp = pt_response["populartimes"]
		# pprint.pprint(pop_time_resp)
		Queries[i].assignPopularTimes(pop_time_resp)
		# print(Queries[i].populartimes)

def print_Queries(Queries):
	for i in range(len(Queries)):
		print(Queries[i].name)
		print(Queries[i].lat)
		print(Queries[i].long)
		print(Queries[i].populartimes)
def getCurrentBusy(Query):
	week_day = datetime.datetime.today().weekday()
	hour= datetime.datetime.now().hour
	print("week day "+str(week_day+1)+" hour: "+str(hour))
	return Query.populartimes[str(week_day+1)][hour]


def search_in_range(s_range,Queries,Users,firebase):
	#go through all Query, one by one and find which elements in Users is within range
	lat_q=0
	long_q=0
	lat_u=0
	long_u=0
	distance_geo=0
	distance_circle=0
	# print('QUERIES: \n')
	# for i in range(len(Queries)):
	# 	print(Queries[i].name)	
	# 	print(Queries[i].lat)	
	# 	print(Queries[i].long)	

	# print('USERS: \n')
	# for i in range(len(Users)):
	# 	print(Users[i].key)	
	# 	print(Users[i].lat)	
	# 	print(Users[i].long)	

	for q in range(len(Queries)):
		print('here is q')
		print(q)
		lat_q=Queries[q].lat
		long_q=Queries[q].long
		for j in range(len(Users)):
			lat_u=Users[j].lat
			long_u=Users[j].long
			# distance=haversine(long_q, lat_q, long_u, lat_u)
			distance_geo=geodesic((lat_q,long_q), (lat_u,long_u)).km
			#distance_circle=great_circle((lat_q,long_q), (lat_u,long_u)).km
			#print('distance geodesic i: %d, lat: %f, long: %f,j: %d lat: %f, long: %f is: %f' % (i,lat_q,long_q,j,lat_u,long_u,distance_geo))
			#print('distance great circle i: %d,j: %d is: %f' % (i,j,distance_circle))
			if(distance_geo<=s_range):
				Queries[q].add_one_person()
				Queries[q].add_age(Users[j].age)
		Queries[q].average_age()
				#Queries[q].avg_age()
	print('number of people list: \n')
	for i in range(len(Queries)):
		print(Queries[i].name)
		print(Queries[i].ppl)	
		print(Queries[i].avg_age)	
	#*********************************************This code will extract from the database all the queries to get their info
	# result = firebase.get('/query',None)
	# num_query = len(result)
	# # print(result)
	# json_object = json.dumps(result)
	# a = json.loads(json_object)
	# # print(a)
	# for i in range(num_query):
	# 	print(Queries[i].name)
	# 	print(a[Queries[i].key['name']]['name'])
	# 	print(a[Queries[i].key['name']]['lat'])
	# 	print(a[Queries[i].key['name']]['long'])
	#*********************************************END EXTRACTION

	#******* GET ALL THE PEOPL FROM THE DATABASE

	#******* END GETTING ALL PEOPLE FROM DATABASE


api_key='8auFVhR1WTiqecfzntGHWEMDMHRpkvSZfIR17sNFImRok0yz22MAHyULEHpktxl-6yLHYBkB4zVETSQrk32YQd9aJBNRdL_N3LQ_RuE2f6Ac31LoP16rGtYJVCSZW3Yx'
yelp_api = YelpAPI(api_key)
firebase = firebase.FirebaseApplication('https://fir-project0-f4e17.firebaseio.com/', None)

#coffee near 34 Lacona Cres.
#search_results=yelp_api.search_query(categories= 'coffee,coffeeroasteries,coffeeshops', 
#	latitude=43.9407282,longitude=-79.4403567, radius=5000, limit=10)

#BARS and Clubs
initialize=0
routine = 0
routine_queries = 0
live_test = 0
google_api_test=0
update_busy_max = 1


if(initialize == 1):
	search_results=yelp_api.search_query(categories= 'bars,nightlife', 
		latitude=43.648360,longitude=-79.388940, radius=1000, limit=50)
	Queries=[]
	Users = []

	Queries=store_query(search_results,initialize,"/new_query") #initializes the queries into the database
if(update_busy_max==1):
	currMax = getBusyMax(firebase,'/g_api_venues')
	setBusyMax(firebase,'/g_api_venues',currMax)

if(google_api_test == 1):
	search_results=yelp_api.search_query(categories= 'bars,nightlife', 
		latitude=43.648360,longitude=-79.388940, radius=1000, limit=10)
	Queries=[]
	Users = []

	Queries=store_query(search_results,initialize,'/g_api_venues') #initializes the queries into the database
	# for i in range(len(Queries)):
	# 	curBusy=getCurrentBusy(Queries[i])
	# 	print(Queries[i].name+" Busy scale: "+ str(curBusy))
	#print_Queries(Queries)
	#get_popular_time(Queries,firebase)
	#upload_popular_time(Queries,firebase,'/g_api_venues/')

if(routine_queries==1):
	for i in range(0,30):
		modify_queries(Queries,firebase) #changes the people and average age randomly of the queries
		time.sleep(15)

#print(search_results)
if(routine==1):
	for i in range(0,10):

		make_users(firebase,Queries) #creates random users and adds them to firebase
		Users=get_users(firebase,'/new_users')  #get all users from firebase

		#**************************************iterate through all the users!! ********
		#for i in range(len(Users)):
		#	print(Users[i].key)
		#	print(Users[i].lat)
		#	print(Users[i].long)
		#	print(Users[i].age)
		#**************************************iterate through all the users!! ********

		s_range=0.1 #distance in km
		# get_users(firebase)
		search_in_range(s_range,Queries,Users,firebase) #assign people stats to queries
		upload_people(Queries,firebase,'/new_query/') #modify query results in firebase based on people in the area
		clear_users(firebase) #remove all users from firebase
		time.sleep(15)

if(live_test == 1):
	clear_branch(firebase,'/venue_v1') #clear all venues!

	Venues = []
	Users = []
	venue_addresses=["34 Lacona Cres. Richmond Hill","32 Lacona Cres. Richmond Hill","Four Winds Parkette Richmond Hill", "132 Nantucket Dr. Richmond Hill","136 Nantucket Dr. Richmond Hill", "42 Inverhuron St. Richmond Hill", 
	"156 Nantucket Dr. Richmond Hill", "23 Park Cres. Richmond Hill", "449 Sunset Beach Rd. Richmond Hill", "377 Sunset Beach Rd. Richmond Hill", "130 English Oak Dr. Richmond Hill"]
	geolocator = GoogleV3(api_key="AIzaSyAEKX3BdRL6ewBpaPIAUVskrbrQV761wvo")

	for addrs in venue_addresses:
		locations = geolocator.geocode(addrs)
		if locations:
			#print(locations.latitude)  # select first location
			#print(locations.longitude)
			venue=create_venue(firebase,addrs,locations.latitude,locations.longitude,'/venue_v1') #populate venues with addresses
			Venues.append(venue)
	while(1==1):
		Users=get_users(firebase,'/users_v1')  #get all users from firebase

		#**************************************iterate through all the users!! ********
		for i in range(len(Users)):
			print(Users[i].key)
			print(Users[i].lat)
			print(Users[i].long)
			print(Users[i].age)
		#**************************************iterate through all the users!! ********

		s_range=0.01 #distance in km
		# get_users(firebase)
		search_in_range(s_range,Venues,Users,firebase) #assign people stats to queries
		upload_people(Venues,firebase,'/venue_v1/') #modify query results in firebase based on people in the area
		clear_venues_people(Venues)
		time.sleep(30)


# for venue in Venues:
	# 	print(venue.name)

#locations = geolocator.geocode("34 Lacona Cres. Richmond Hill")
# if locations:
#     print(locations.latitude)  # select first location
#     print(locations.longitude)  # select first location

#else:
#	make_users(firebase,Queries)	
#	clear_users(firebase)




