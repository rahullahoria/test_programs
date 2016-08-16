#!/usr/bin/python
import time
import json
import os
import time
import requests
from gi.repository import Gtk, Wnck

usageInMin = {'startAt':int(time.time())}
programInstance = {'Iceweasel': -2,'PhpStorm 10.0.3':0}
Gtk.init([])  # necessary if not using a Gtk.main() loop
url = 'http://api.bulldog.shatkonlabs.com/usage/1'
Gtk.main_iteration()
logFileName = '/var/log/bulldog/usage.log'
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

	if os.path.isfile(logFileName) :
		with open(logFileName) as data_file:    
	    		try:   
				usageInMin = json.load(data_file)
			except ValueError:  # includes simplejson.decoder.JSONDecodeError
				pass    				
				#print 'Decoding JSON has failed'
	open(logFileName, 'w').close()
	f = open(logFileName,'w')

	try:
		screen = Wnck.Screen.get_default()
		screen.force_update()  # recommended per Wnck documentation

		window_list = screen.get_windows()
		##print len(window_list)
		active_window = screen.get_active_window()

		program = active_window.get_name().split('-')[-1].strip()
		##print program

		instance = "unknown"	
		try:		
			if programInstance.has_key(program):
				i = programInstance[program]
			else :
				i = 0		
			instance = active_window.get_name().split('-')[i].strip()
		except IndexError:
			program = active_window.get_name().split('-')[-1].strip()

		if usageInMin.has_key(instance):
			usageInMin[instance]['time'] += 60
			if usageInMin[instance]['files'].has_key(active_window.get_name()):
				usageInMin[instance]['files'][active_window.get_name()] += 60
			else :
				usageInMin[instance]['files'][active_window.get_name()] = 60
		else :
			usageInMin[instance] = {}
			usageInMin[instance]['time'] = 60
			usageInMin[instance]['program'] = program
			usageInMin[instance]['files'] = {}
			usageInMin[instance]['files'][active_window.get_name()] = 60
	


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

		usageInMin['lastUpdate'] = int(time.time())
		#print(json.dumps(usageInMin))
		#print "\n\n\n"
		screen = window_list = active_window = ""
		Wnck.shutdown()
	except:
		usageInMin['lastUpdate'] = int(time.time())
		screen = window_list = active_window = ""
		Wnck.shutdown()
		pass
	f.write(json.dumps(usageInMin))
	f.close()
	time.sleep(60)

