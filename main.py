import requests, re, sys, pdb, codecs
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup
from form import Form

#dict to keep all cached pages
cachedPages = {}

#specify max recurrency depth
maxDepth = 1

#dict to keep the recovered forms
forms = {}

def getSite(url, allowedDomain, currentDepth):
	
	#try to get the site from url
	try: 
		response = requests.get(url)	
	except requests.exceptions.InvalidURL:
		print("Could not get url")
		cachedPages.update({url:False})
		return

	print(url+' '+str(response.status_code))

	#add current url to the dict
	cachedPages.update({url:response.text})

	#return if we reached our max depth
	if(currentDepth > maxDepth):
		return

	#parse the page to look for new links
	soup = BeautifulSoup(response.text)

	#look for new urls on downloaded site
	for u in soup.findAll('a', href=True):

		recoveredUrl = u['href']
		try:
			parsed = urlparse(recoveredUrl)
		except ValueError:
			print("Recovered an invalid url")
			continue

		#url used to make further requests, basically original url stripped from GET parameters
		fullLink = parsed.scheme+'://'+parsed.netloc+parsed.path		

		#used for the same-domain check
		domain = parsed.hostname

		if(domain == allowedDomain and not cachedPages.has_key(fullLink)):
			getSite(fullLink, allowedDomain, currentDepth+1)

def main():

	root = sys.argv[1]

	try:
		parsedRoot = urlparse(sys.argv[1])
	except ValueError:
		print("Invalid URL");
		exit


	#get all pages from specified domain recursively
	print("Caching pages...")
	getSite(root, parsedRoot.hostname, 0)
	print("Finished, got "+str(len(cachedPages.keys()))+" pages")

	#iterate over cachedPages
	for p in cachedPages.items():
		url = p[0]
		rawData = p[1]

		parsedRaw = BeautifulSoup(p[1])

		for f in parsedRaw.findAll('form'):

			#check if action is set
			try:
				action = f['action']
			except KeyError:
				continue

			if(action[0:4] != 'http'):
				action = url+action

			forms.update({action:Form(f, action, url)})


	for form in forms.items():
		f = codecs.open('output/'+form[0].replace('/', '\\')+'.py', 'w+', 'utf-8')
		script = form[1].generateScript()
		f.write(script)
		f.close()


if __name__ == "__main__":
    main()