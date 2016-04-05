from BeautifulSoup import BeautifulSoup

class Form:

	requestedFrom = ""

	url = ""
	rawData = ""

	inputs = []

	method = ""
	def __init__(self, rawData, url, requestedFrom):

		self.rawData = rawData
		self.url = url;
		self.requestedFrom = requestedFrom

		#if method attribute is not present, get request is assumed
		try:
			self.method = self.rawData['method']
		except KeyError:
			self.method = "get"


		self.inputs = self.rawData.findAll('input')



	def generateScript(self):
		request = "import requests\n"
		request += "\n#requested from "+self.requestedFrom+"\n\n"

		request += "url = '"+self.url+"'\n"

		request += "payload = {\n"
		for i in self.inputs:

			placeholder = 'data'

			#try to get default placeholder
			try:			
				placeholder = i['placeholder']
			except KeyError:
				#try again to get the type
				try:
					placeholder = i['type']
				except KeyError:
					pass

			try:
				request += "	'"+i['name']+"':'"+placeholder+"',\n"
			except KeyError:
				continue

		request += "}\n"

		if(self.method.lower() == "post"):
			request += "r = requests.post(url, data=payload)\n"
		else:
			request += "r = requests.get(url, data=payload)\n"

		request += "print(r.status_code)\n"
		request += "print(r.text)\n"

		return request
		
