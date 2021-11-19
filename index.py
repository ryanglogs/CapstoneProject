#!/Python38/python.exe

from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
import tweepy
import datetime
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account
import sys
import re
import praw
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import pandas as pd
import cgi
import cgitb 
cgitb.enable()

form = cgi.FieldStorage()
query = form.getvalue('query')
businessQuery = form.getvalue('businessquery')
locationQuery = form.getvalue('locationquery')
numResults = int(form.getvalue('numresults'))
sortValue = form.getvalue('sortBy')

print("Content-Type: text/html")
print("")
print("<link rel=stylesheet type=text/css href=./capstone.css>")
print("<TITLE>Search Results</TITLE>")
results = []


def google_maps_api(): #this handles google maps api
	# API key here
	api_key = ''

	# Google Place URL
	url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

	url2 = "https://www.google.com/maps/embed/v1/search?"

	

	# get method of requests module
	# return response object
	r = requests.get(url + 'query=' + businessQuery + '-in-' + locationQuery +
		'&key=' + api_key)

	#r2 = requests.get(url2 + 'key=' + api_key + '&q=' + query + '+in+' + query2)

	urlbuild = (url2 + 'key=' + api_key + '&q=' + businessQuery + '+in+' + locationQuery)
	
	print("<fieldset class=results>")
	print("<legend><b>Google Maps Results</b></legend>")
	
	print("<iframe style=float:left")
	print("width=675")
	print("height=475")
	print("frameborder=0 style=border:0")
	print("src=",urlbuild, "allowfullscreen>")		
	print("</iframe>")

	#print(r.text)  

	# json method of response object convert
	#  json format data into python format data
	x = r.json()

	# now x contains list of nested dictionaries
	# we know dictionary contain key value pair
	# store the value of result key in variable y
	y = x['results']

	print("<p> &#160&#160&#160&#160&#160&#160 Results: <br>")
	# keep looping upto length of y
	for i in range(len(y)):
	
	# Print value corresponding to the
	# 'name' key at the ith index of y
		print("&#160&#160&#160&#160&#160&#160",y[i]['name'])
		print("<br>")
	
	print("</p>")
	print("</fieldset>")

def spotify_api(): #this handles spotify api
	auth_manager = SpotifyClientCredentials('', '')
	sp = spotipy.Spotify(auth_manager=auth_manager)
	spotifyResults = sp.search(query,limit=numResults,offset=0,type='track',market=None)
	results.append("SPOTIFY RESULTS")
	print("<fieldset class=results>")
	print("<legend><b>Spotify Results</b></legend>")
	# IMAGE URL: songs['album']['images'][0]['url']
	# SONG URL: songs['album']['external_urls']['spotify']
	print("<p><br>")
	for i in range(numResults):
		songs = spotifyResults['tracks']['items'][i]
		print('<img src= {0} width=300 height=300> <br>'.format(songs['album']['images'][0]['url']))
		print('Album: <a href= {0} > {1} </a><br>'.format(songs['album']['external_urls']['spotify'], songs['album']['name']))
		results.append('Album: {0}'.format(songs['album']['name']))
		print('Artist: <a href= {0} > {1} </a><br>'.format(songs['artists'][0]['external_urls']['spotify'],songs['album']['artists'][0]['name']))
		results.append('Artist: {0}'.format(songs['album']['artists'][0]['name']))
		print('Song: <a href= {0} > {1} </a><br>'.format(songs['external_urls']['spotify'], songs['name']))
		results.append('Song: {0} <br>'.format(songs['name']))
		print("Song Preview: <br>")
		print('<audio controls> <source src= {0}> </audio>'.format(songs['preview_url']))
		print("<br><br>")
	print("</p>")
	print("</fieldset>")

def youtube_Scraper(): #this handles youtube api
	scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

	results.append("YOUTUBE RESULTS")

	api_service_name = "youtube"
	api_version = "v3"
	api_key = ""
	client_service_file = ""
	client_secrets_file = ""

	# Get credentials and create an API client
	flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
		client_secrets_file, scopes)
	
	credentials = service_account.Credentials.from_service_account_file(client_service_file, scopes=scopes)
	
	youtube = googleapiclient.discovery.build(
		api_service_name, api_version, credentials=credentials)

	request = youtube.search().list(
		part="snippet",
		channelType="any",
		maxResults=numResults+1,
		q=query
	)

	response = request.execute()
	responseDF = pd.DataFrame(response['items'])
	
	titleArray = []
	index = 0
	for title in responseDF['snippet']:
		titleArray.append(title['title'])
	
	print("<fieldset class=results>")
	print("<legend><b>Youtube Results</b></legend>")
	print("<p><br>")
	for value in responseDF['id']:
		#print(type(value))
		if value['kind'] == 'youtube#video':
			#print(value['videoId'])
			#print('youtube.com/watch?v={0}'.format(value['videoId']))
			results.append('https://youtube.com/watch?v={0} - {1}'.format(value['videoId'], titleArray[index]))
			print('Video Title and Link: <a href= https://youtube.com/watch?v={0} >'.format(value['videoId']), handle_emoji(titleArray[index]), "</a>")
			print("<br>")
			print("<br>")
			index += 1
		
	print("</p>")
	print("</fieldset>")
	
def handle_emoji(inputString):#this method handles emojis from twitter so they are printable in html
	
	#encode the text of the input string so that the emojis are in the form '\\U000XXXXX'
	encoded_text = inputString.encode("unicode-escape")
	
	#splits the text into an array of each word in the text
	encoded_text_array = encoded_text.split(b" ")
		
	rebuiltString = ""
	
	#this loops through each word in the array an determines wether it is an emoji or not
	for string in encoded_text_array:
		#print("<p> current string: ", string, "</p>")
		
		#since emojis dont have a space between them in the array, if there are consecutive emojis the emojis 
		#are in the form "\\U000XXXXX\\U000XXXXX\\U000XXXXX" so a new array needs to split the emojis into seperate emojis
		if string.startswith(b'\U0') or  string.startswith(b'\u'):
			emojiArray = string.replace(b'\U000',b' ').replace(b'\u',b' ').split(b' ') ##removes the unicode portion of the emojis and then splits them into a seperate array
			for value in emojiArray:
				value = value.decode('utf-8')#this converts the emojis from the form b'XXXXX' to just XXXXX
				if len(value) == 5:
					string = '&#x{0};'.format(value)#this concatonates the value of the emoji into a format that the html page can understand
					rebuiltString = rebuiltString + " " + string #concatonates each value of the array into a full string to be returned and printed
		if type(string) is bytes:
			#the non emoji values are still of type bytes so they need to be reconverted to string to print them out on the webpage
			rebuiltString = rebuiltString + " " + string.decode('utf-8')#concatonates each value of the array into a full string to be returned and printed
	try:
		return rebuiltString
	except UnicodeEncodeError:
		print("<p>emoji error</p>")

def twitter_Scraper():#this method handles the twitter api

	# # this is to authenticate that i have a developer twiter account and is required to use twitter api's
	# # the CONSUMER_KEY/SECRET are stored in another file
	auth = OAuthHandler(, )
	auth.set_access_token(, )

	api = API(auth)
	error = False
	results.append("TWITTER RESULTS")
	print("<fieldset class=results>")
	print("<legend><b>Twitter Results</b></legend>")
	try:
		# get_user() returns a user object that contains info about the specified twitter user
		# like name, screen name, location, bio, twitter id, url, etc.
		
		profile_info = api.get_user(query)
		
		# creates empty array that will store the tweets
		tweets = []
		# loops through the most recent 5 five tweets made by the given user
		# and adds them to the array that contains the tweets
		for tweet in Cursor(api.user_timeline, id=profile_info.screen_name).items(numResults):
			tweets.append(tweet)
			
		# If a user doesnt give their location, this will replace null with no location given
		location = profile_info.location
		if location == '':
			location = "No location Given"
		
		
		# prints basic user info
		print("<h3>Profile info:<br> </h3>")
		print("<p>")
		print("Name: ")
		results.append(handle_emoji(profile_info.name))
		print(handle_emoji(profile_info.name))
		print("<br>Screen Name: ", profile_info.screen_name)
		results.append(profile_info.screen_name)
		print("<br>Location: ", location)
		results.append(location)
		print("<br>Bio: ")
		results.append(profile_info.description)
		print(handle_emoji(profile_info.description))
		print("</p>")
		
		#prints recent five tweets from the user
		print("<h3>Recent five tweets:<br> </h3>")
		
		for tweet in tweets:
			try:
				print("<p>", handle_emoji(tweet.text) , "<br></p>")
				results.append(handle_emoji(tweet.text))
			except UnicodeEncodeError:
				print("<p> emoji error </p>")
				continue
			
	except tweepy.TweepError as e:
		if str(e.response) == "<Response [401]>": #if the user is private
			print("<p>This user has privated their account</p>")
			results.append("private twitter user")
		elif e.api_code == 50:
			print("<p>No users found matching the query</p>")
		elif e.api_code == 63:
			print("<p>This user has been suspended</p>")
			results.append("suspended twitter user")
		else:
			print("<p>", e.response, "</p>")

	if (error):
		print("<h3>No tweets found relating to search</h3><br>")
	else:
		print("<h3>Tweets relating to search: </h3>")		

		tweet_info = api.search(q=query, count=numResults)
		
		for tweet in tweet_info:
			try:
				print("<p>", handle_emoji(tweet.text) , "<br></p>")
				results.append(handle_emoji(tweet.text))
			except UnicodeEncodeError:
				print("<p> emoji error </p>")
				continue
	print("</fieldset>")

def reddit_Scraper():#this method handles the reddit api
		
	reddit = praw.Reddit(client_id="",#my client id
                     client_secret="",  #your client secret
                     user_agent="", #user agent name
                     username = "",     # your reddit username
                     password = "")     # your reddit password

	sub = ['All']  # make a list of subreddits you want to scrape the data from
	results.append("REDDIT RESULTS")
	for s in sub:
		subreddit = reddit.subreddit(s)   # Chosing the subreddit


		#query = ['Gaming']

		for item in query:
			post_dict = {
			"title" : [],
			"score" : [],
			"id" : [],
			"url" : [],
			"comms_num": [],
			"created" : [],
			"body" : []
			}
			comments_dict = {
			"comment_id" : [],
			"comment_parent_id" : [],
			"comment_body" : [],
			"comment_link_id" : []
			}
			for submission in subreddit.search(query,sort = sortValue,limit = numResults):
				post_dict["title"].append(submission.title)
				post_dict["score"].append(submission.score)
				post_dict["id"].append(submission.id)
				post_dict["url"].append(submission.url)
				post_dict["comms_num"].append(submission.num_comments)
				post_dict["created"].append(datetime.datetime.utcfromtimestamp(submission.created))
				post_dict["body"].append(submission.selftext)

	
	post_array = pd.DataFrame(data=post_dict)
		
	print("<fieldset class=results>")
	print("<legend><b>Reddit Results</b></legend>")
	print("<p>")
	try:
		for i in range(0,numResults):
			print("<br>")
			print("Title/URL: <a href=",post_array.loc[i,'url'],">", post_array.loc[i,'title'], "</a>")
			results.append(post_array.loc[i,'url'])
			print("<br>")
			print("Date created: ", post_array.loc[i,'created'])
			results.append(post_array.loc[i,'created'])
			print("<br>")
	except KeyError:
		print("<h3>No Results Found</h3>")
	print("<br>")
	print("</p>")
	print("</fieldset>")

def download_Results():
	resultsDF = pd.DataFrame(results)
	resultsDF.to_csv("capstoneSearchResults.csv")


if form.getvalue("twitter"):
	twitter_Scraper()
	
if form.getvalue("reddit"):
	reddit_Scraper()
	
if form.getvalue("youtube"):
	youtube_Scraper()

if form.getvalue("spotify"):
	spotify_api()

if form.getvalue("googlemaps"):
	google_maps_api()

#download_Results()