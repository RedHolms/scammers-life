import requests
from .exceptions import *

API_URL = 'https://api.vk.com/'
API_METHOD_URL = API_URL + 'method/'

class ApiSession(object):
	def __init__(self, token: str, version: str = '5.131', httpSession: requests.Session = None) -> None:
		self.token = token
		self.v = version
		self.httpSession = httpSession if type(httpSession) == requests.Session else requests.Session()
	def executeMethod(self, methodName: str, params: dict, requestMode: str = 'get', returnRaw: bool = False, safeMode: bool = False):
		if not 'v' in params: params['v'] = self.v
		if not 'access_token' in params: params['access_token'] = self.token

		response = self.httpSession.request(requestMode, API_METHOD_URL + methodName, params=params)

		if response.status_code not in range(200, 299):
			raise ConnectionError(response)

		json = response.json()

		if 'error' in json:
			if not safeMode:
				raise InvalidVkApiResponse(json)
			else:
				return json

		return (response if returnRaw else json['response'])