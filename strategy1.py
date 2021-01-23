import json 
import pprint 
#import pandas as pd 
import operator #used with indicators

from datetime import datetime #historical price and look back
from datetime import timedelta #lets you add time and take away time to it
from configparser import ConfigParser #for reading config file

from pyrobot.trades import Trade
from pyrobot.robot import PyRobot #import pyrobot object
from pyrobot.indicators import Indicators 

# Read the config file

config = ConfigParser()
config.read("config/config.ini")

# Read the different values

CLIENT_ID = config.get("main", "CLIENT_ID")
REDIRECT_URI = config.get("main", "REDIRECT_URI")
JSON_PATH = config.get("main", "JSON_PATH")
ACCOUNT_NUMBER = config.get("main", "ACCOUNT_NUMBER")

print(REDIRECT_URI)