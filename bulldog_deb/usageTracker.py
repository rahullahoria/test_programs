#!/usr/bin/python
import time
import json
import os
import time
import requests
from gi.repository import Gtk, Wnck
import pymouse
import getpass

pc_username = getpass.getuser()
mPosition = pymouse.PyMouse().position()
userConfFile = "/home/spider-ninja/.userBullDogConf"
userId = "1"
usageInMin = {'startAt':int(time.time())}
programInstance = {'Firefox': -2, 'Iceweasel': -2,'PhpStorm 10.0.3':0}
Gtk.init([])  # necessary if not using a Gtk.main() loop
url = 'http://api.bulldog.shatkonlabs.com/usage/'+ userId
Gtk.main_iteration()
logFileName = '/var/log/bulldog/usage.log'
program = ""
instance = ""
fileName = ""
sleepTime = 60

def userActive():
	global mPosition
	if mPosition == pymouse.PyMouse().position():
		return False
	mPosition = pymouse.PyMouse().position()
	return True
	

def loadLogFile():
	global logFileName
	global usageInMin
	if os.path.isfile(logFileName) :
		with open(logFileName) as data_file:    
			try:   
				usageInMin = json.load(data_file)
			except ValueError:  # includes simplejson.decoder.JSONDecodeError
				pass    				
				#print 'Decoding JSON has failed'
	
	

def writeTime():
	global usageInMin
	global program
	global fileName
	global program
	global sleepTime
	if usageInMin.has_key(instance):
		usageInMin[instance]['time'] += sleepTime
		if usageInMin[instance]['files'].has_key(fileName):
			usageInMin[instance]['files'][fileName] += sleepTime
		else :
			usageInMin[instance]['files'][fileName] = sleepTime
	else :
		usageInMin[instance] = {}
		usageInMin[instance]['time'] = sleepTime
		usageInMin[instance]['program'] = program
		usageInMin[instance]['files'] = {}
		usageInMin[instance]['files'][fileName] = sleepTime
			

def syncWithServer():
	global usageInMin
	global logFileName
	global pc_username
	usageInMin['pc_username'] = pc_username
	if usageInMin.has_key('startAt') :
		if ((int(time.time()) - usageInMin['startAt']) >= 120):
			try :
				response = requests.post(url, data=json.dumps(usageInMin))
				if response.status_code == 200:
					open(logFileName, 'w').close()
					usageInMin = {'startAt':int(time.time())}
			except response.exceptions.Timeout:
				# Maybe set up for a retry, or continue in a retry loop
				pass
			except response.exceptions.TooManyRedirects:
				pass
				# Tell the user their URL was bad and try a different one
			except response.exceptions.RequestException as e:
				# catastrophic error. bail.
				pass
			#print response.status_code		
	

	else:
		usageInMin['startAt'] = int(time.time())


def loadProgramInstnaceFile():
	global instance
	global fileName
	global program
	
	screen = Wnck.Screen.get_default()
	screen.force_update()

	window_list = screen.get_windows()
	active_window = screen.get_active_window()
	program = active_window.get_application().get_name().split('-')[-1].strip()

	instance = "unknown"
	try:		
		if programInstance.has_key(program):
			i = programInstance[program]
		else :
			i = 0		
		instance = active_window.get_name().split('-')[i].strip()
	except IndexError:
		program = active_window.get_name().split('-')[-1].strip()
	screen = window_list = active_window = ""
	Wnck.shutdown()


	
'''
if os.path.isfile(logFileName) :
	with open(logFileName) as data_file: 
		try:   
    			usageInMin = json.load(data_file)
		except ValueError:  # includes simplejson.decoder.JSONDecodeError
    			pass
			#print 'Decoding JSON has failed'

if usageInMin.has_key('lastUpdate') :	
	if ((int(time.time()) - usageInMin['lastUpdate']) <= 10):		
		#print "i want to exit"		
		os._exit(1)
'''
while 1:

	loadLogFile()
	print(json.dumps(usageInMin))
	print "\n\n\n"
	if userActive():
		f = open(logFileName,'w')

		try:
			loadProgramInstnaceFile()

			writeTime()

			syncWithServer()

			usageInMin['lastUpdate'] = int(time.time())
		except:
			usageInMin['lastUpdate'] = int(time.time())
			pass
		open(logFileName, 'w').close()
		f.write(json.dumps(usageInMin))
		f.close()
	time.sleep(sleepTime)

