import requests
import argparse
from time import sleep
import os
import sys

version = '0.1alpha'

parser = argparse.ArgumentParser(prog='RD-tool',formatter_class=argparse.RawTextHelpFormatter, 
description='This python script is the work of @spookyahell (Github username).\n'+
'Unlawful distribution or even usage is strictly prohibited.\nPremission is required.\n'+
'DISCLAIMER: I am not responsible for any damage caused by this script.\n'+
'Keep all pets away and don\'t let them near you while you\'re working with this script.\n'+
'You have been warned! Nothing is impossible when Donald Trump is president.\n(Well besides a reasonable president of course and a reasonable government and etc. etc.))')
parser.add_argument('urls',
                    help='URL from any supported filehost', metavar='URL', nargs='*')
parser.add_argument('--addMagnet',
                    help='add a magnet')
parser.add_argument('--apitoken', '-t',
                    help='set the API token, get it from real-debrid.com/apitoken')
parser.add_argument('--silent', '-s',
                    help='silent mode', action='store_true')
parser.add_argument('--silent-link-only', '-slo',
                    help='silent link only', action='store_true')
parser.add_argument('--textfile', '-txt',
                    help='Create a textfile with the links', action='store_true')
args = parser.parse_args()

if not args.silent and not args.silent_link_only:
	print('Welcome to the unofficial RD tool!')

#~ jar1 = requests.cookies.RequestsCookieJar()
#~ jar1.set('', 'VWU5Zvhizf')
if (args.apitoken != None):
	tokenfile = open('RDtoken.txt','w') 
	tokenfile.write(args.apitoken)
	tokenfile.close()
	print('Token saved')
else:
	if (os.path.isfile('RDtoken.txt')):
		if not args.silent and not args.silent_link_only:
			print('No token specified, but saved token found')
		
if (os.path.isfile('RDtoken.txt')):
	tokenfile = open('RDtoken.txt','r') 
	apitoken = tokenfile.readline()
	if not args.silent and not args.silent_link_only:
		print(f'Using token {apitoken}...')
		print()
else:
	print('You must specify a token via --apitoken first.')
	sys.exit(1)

headers = {'Authorization': f'Bearer {apitoken}'}


if len(args.urls) == 0:
	if not args.silent and not args.silent_link_only:
		print('No links to process...')
else:
	if args.textfile:
		links = open('RDlinks.txt','w') 
		linkvalues = []

for url in args.urls:
	data = {'link': url, 'password':''}
	r = requests.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', data = data, headers = headers)
	linkdata = r.json()
	if not args.silent_link_only:
		print(linkdata['filename']+'\n'+linkdata['download'])
	else:
		print(linkdata['download'])
	if args.textfile:
		linkvalues.append(linkdata['download'])
		
if args.textfile:
	links.write('\n'.join(linkvalues))
	links.close()

if (args.addMagnet != None):
	postdata = {'host':'real-debrid.com','split':'2', 'magnet':args.addMagnet}
	r = requests.post('https://api.real-debrid.com/rest/1.0/torrents/addMagnet', 
		data = postdata, headers = headers, verify=False)
	#~ print(r.text)
	#~ 
	cookies = f'https=1; lang=de; cookie_accept=y; auth={apitoken}; session-set=true'
	
	errorcodes = {202 : 'Action already done', 400 : 'Bad request',
		401: 'Bad token', 403:  'Permession deinied, check if premium', 404 : 'Invalid file ids'}
	
	def getTorrentInfo():
		r2 = requests.get('https://api.real-debrid.com/rest/1.0/torrents/info/'+r.json()['id'], 
			headers = headers, verify=False)
		print(r.json()['id'])
		jsonfiles = r2.json()['files']
		if  len(jsonfiles) == 0:
			print('This is weired. Maybe it does not work as well as the developer thought?')
		else:
			for idx, item in enumerate(jsonfiles):
				print(f'{idx+1} '+item['path'])
			print('Okay, now we\'ll need a comma seperated list of indexes for files you want.')
			selectedfiles = input('List of IDs or ALL: ') 
			postdata = {'files': selectedfiles}
			r3 = requests.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/'+r.json()['id'], data = postdata, headers = headers, verify=False)
			if r3.status_code == 204:
				print('Yay, torrent has been added and will now be downloaded')
			else:
				error = errorcodes[status_code]
				print(f'Oops! Error: {error}')
				
	def checkForFilesAvailable():
		r2 = requests.get('https://real-debrid.com/ajax/torrent_files.php?id='+r.json()['id'], headers = {'Cookie':cookies,'X-Requested-With':'XMLHttpRequest'})
		if 'setInterval' in r2.text:
			print('Sleeping for 5 seconds...')
			sleep(5)
			print('Checking if files available...')
			checkForFilesAvailable()
		else:
			print('Okay, seems like the torrent may actually be available.')
			getTorrentInfo()
	checkForFilesAvailable()
	
	print(r.json()['id'])
else:
	if not args.silent and not args.silent_link_only:
		print()
		print('No magnet to add')