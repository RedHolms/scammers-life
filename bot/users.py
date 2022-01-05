class User(object):
	def __init__(self, id: int, api, env: dict = {}):
		self.id = id
		self.env = env
		
		self.api = api

		self.registed = False
		self.nickname = ''

		self.last_event = 0

		self.name = ''
		self.surname = ''

		self.initialized = False
	
	def SendMessage(self, **kwargs):
		if 'random_id' not in kwargs:
			kwargs['random_id'] = 0
		kwargs['peer_id'] = self.id

		return self.api.executeMethod('messages.send', kwargs)
