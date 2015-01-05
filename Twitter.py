#!/usr/bin/python

import requests, json, sys , logging, os, time
from datetime import datetime
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from requests_oauthlib import OAuth1
from pymongo import MongoClient

CONSUMER_KEY = "Yo7a6XaUwMYhEOmK94UqZMSE1"
CONSUMER_SECRET = "Vc62lpogyRf3OPib3V5mm2NzU0k1Pv3OiPLpPgGJMzrlxkQhn8"
ACCESS_KEY = "2940430290-Q0lbmF0IBM8jlagkKrxW7rJLGGpJHw4MLHSMgT4"
ACCESS_SECRET = "vd24a9v4HVXB3NirgJxC18jxuXxnYwsbKWXjRXec4Gl6r"

#return the sinceID to get latest tweets
def getSinceID():
	try:
		file = open('since_ID.txt','r')
		data = file.read()
		return data
	except:
		return 0

#return tweets as a json object
def getTweets():
	url = 'https://api.twitter.com/1.1/search/tweets.json'
	auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
	last_tweet_id = int(getSinceID())	
	payload = {'q': '#PresPollSL', 'count': 200, 'since_id': last_tweet_id }
	response = requests.get(url, auth=auth, params=payload)
	#return json.loads(response.text), last_tweet_id
	return response.json()['statuses']

def cleanStatement(sentence):
	array = sentence.split()
	cleanSentence = ""
	for element in array:
		try:
			element.decode('ascii')
			cleanSentence = cleanSentence + element + " "
		except:
			cleanSentence = cleanSentence+ ""
	
	return cleanSentence
	

	
#return the sentiment as a json object
def getSentiment(text):
	result = vaderSentiment(cleanStatement(text))
	return result
	

#save to mongodb database		
def saveToDB( tweet_json):	
	client = MongoClient('mongodb://nishada:110330V@ds031271.mongolab.com:31271/twittersentiment')	
	db = client.twittersentiment.tweets	
	
	for tweet in tweet_json:
		tweets = {'tweet_json': tweet, 'sentiment_json':getSentiment(tweet['text'])}
		db.insert(tweets)	
	client.close()

def updateSinceID(id):
	file = open("since_ID.txt","w")
	file.write(id)
	file.close()
	

while True :
	data = getTweets()
	if len(data) != 0 :
		updateSinceID(data[0]['id_str'])
	saveToDB(data)
	
	time.sleep(60)
