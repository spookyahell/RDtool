import requests
import argparse
from time import sleep
import os
import sys

version = '0.2alpha'

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
parser.add_argument('--multiline-url-input', '-mlui',
                    help='Take urls seperated by newline as input (Enter "RDtool" without quotes as last line to stop taking inputs)', action='store_true')
args = parser.parse_args()

BASE_DOMAIN = "real-debrid.com"
BASE_API_URL = "https://api." + BASE_DOMAIN + "/rest/1.0/"

def debrid_url(url, is_folder = False):
	data = {'link': url, 'password':''}
	if (is_folder):
		r = requests.post(BASE_API_URL + 'unrestrict/folder', data = data, headers = headers)
		linksdata = r.json()
		r.close()
		for link in linksdata:
			debrid_url(link)
	else:
		r = requests.post(BASE_API_URL + 'unrestrict/link', data = data, headers = headers)
		linkdata = r.json()
		r.close()
		if (linkdata.get('error_code') != None):
			print("Error: "+str(linkdata['error_code'])+" - "+linkdata['error'])
		else:
			if not args.silent_link_only:
				print(linkdata['filename']+'\n'+linkdata['download'])
			else:
				print(linkdata['download'])
			if args.textfile:
				linkvalues.append(linkdata['download'])

if not args.silent and not args.silent_link_only:
	print('Welcome to the unofficial RD tool!')

if (args.apitoken != None):
	tokenfile = open('RDtoken.txt','w') 
	tokenfile.write(args.apitoken)
	tokenfile.close()
	print('Token saved')
elif (os.path.isfile('RDtoken.txt')):
	tokenfile = open('RDtoken.txt','r') 
	apitoken = tokenfile.readline().rstrip('\n')
	if not args.silent and not args.silent_link_only:
		print('No token specified, but saved token found')
		print(f'Using token {apitoken}...')
		print()
else:
	print('You must specify a token via --apitoken first.')
	sys.exit(1)

headers = {'Authorization': f'Bearer {apitoken}'}

if args.multiline_url_input:
	print("Enter urls seperated by new line. Once done, send 'RDtool' without quotes as last line.")
	newUrls = []
	inpUrl = ""
	while(inpUrl != "RDtool"):
		if inpUrl != "":
			newUrls.append(inpUrl)
		inpUrl = input().strip()
	args.urls.extend(newUrls)

if len(args.urls) == 0:
	if not args.silent and not args.silent_link_only:
		print('No links to process...')
else:
	if args.textfile:
		links = open('RDlinks.txt','w') 
		linkvalues = []

for url in args.urls:
	debrid_url(url, (url.find("folder") != -1))
	
if args.textfile:
	links.write('\n'.join(linkvalues))
	links.close()

if (args.addMagnet != None):
	postdata = {'host':BASE_DOMAIN,'split':'2', 'magnet':args.addMagnet}
	r = requests.post(BASE_API_URL + 'torrents/addMagnet', 
		data = postdata, headers = headers)
	#~ print(r.text)
	#~ 
	cookies = f'https=1; lang=de; cookie_accept=y; auth={apitoken}; session-set=true'

	errorcodes = {202 : 'Action already done', 400 : 'Bad request',
		401: 'Bad token', 403:  'Permession deinied, check if premium', 404 : 'Invalid file ids'}

	def get_torrent_info():
		r2 = requests.get(BASE_API_URL + 'torrents/info/'+r.json()['id'], 
			headers = headers)
		print(r.json()['id'])
		jsonfiles = r2.json()['files']
		r2.close()
		if  len(jsonfiles) == 0:
			print('This is weired. Maybe it does not work as well as the developer thought?')
		else:
			for idx, item in enumerate(jsonfiles):
				print(f'{idx+1} '+item['path'])
			print('Okay, now we\'ll need a comma seperated list of indexes for files you want.')
			selectedfiles = input('List of IDs or ALL: ') 
			postdata = {'files': selectedfiles}
			r3 = requests.post(BASE_API_URL + 'torrents/selectFiles/'+r.json()['id'], data = postdata, headers = headers, verify=False)
			if r3.status_code == 204:
				print('Yay, torrent has been added and will now be downloaded')
			else:
				error = errorcodes[r3.status_code]
				print(f'Oops! Error: {error}')

	def check_files_availability():
		r2 = requests.get('https://' + BASE_DOMAIN + '/ajax/torrent_files.php?id='+r.json()['id'], headers = {'Cookie':cookies,'X-Requested-With':'XMLHttpRequest'})
		if 'setInterval' in r2.text:
			print('Sleeping for 5 seconds...')
			r2.close()
			sleep(5)
			print('Checking if files available...')
			check_files_availability()
		else:
			print('Okay, seems like the torrent may actually be available.')
			r2.close()
			get_torrent_info()
	check_files_availability()
	
	print(r.json()['id'])
	r.close()
