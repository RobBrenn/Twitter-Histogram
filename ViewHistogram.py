# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:58:34 2015

@author: Confero
"""

import configparser
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
from numpy import pi

print("Retrieving settings")
config = configparser.ConfigParser()
config.read('settings.cfg')

#Start the database
print("Starting database")
client = MongoClient()

username = config.get('database', 'username')
DBNAME = config.get('database', 'name')
COLLECTION = config.get('database', 'user_collection')
db = client[DBNAME]
user_tweets = db[(username + "_timeline4")]

#Array to hold the angles we get
angles = []

#Turns the time in format HH:MM:SS into the time in seconds.
def timeInSeconds(time):
    timeInSeconds = int(time[0:2])*60*60
    timeInSeconds = timeInSeconds + int(time[3:5])*60 
    timeInSeconds = timeInSeconds + int(time[6:7])
    return timeInSeconds

#Turn the seconds into the angle on the clock
def timeInSecondsToClockAngle(timeInSeconds):
    return 2*pi*timeInSeconds/86400
    
cursor = user_tweets.find()
for tweet in cursor:
    angle = timeInSecondsToClockAngle(timeInSeconds(tweet['created_at'][11:19]))
    angles.append(angle)
    
    
#Set up the clock graph
ax = plt.subplot(111, polar=True)

# suppress the radial labels
#plt.setp(ax.get_yticklabels(), visible=False)

# set the circumference labels
ax.set_xticks(np.linspace(0, 2*pi, 24, endpoint=False))
ax.set_xticklabels(range(24))

# make the labels go clockwise
ax.set_theta_direction(-1)

# place 0 at the top
ax.set_theta_offset(pi/2.0)  

n, bins, patches = ax.hist(angles, 24, color='r', normed = 0)
plt.show()
