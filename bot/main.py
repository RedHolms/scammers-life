import logging
log = logging.getLogger('scamLife.bot')

from . import vk_api
from .enums import *
from .users import User

import time

class _HardStop(Exception): pass

class Bot(object):
	def __init__(self, apiSession: vk_api.ApiSession, groupID: int) -> None:
		self.api = apiSession
		self.group_id = groupID

		self.longpoll = vk_api.LongPollServer(self.api.token, self.group_id, self.api)

		self.users = {}

		self.started = False
	
	def Start(self):
		log.debug('Starting...')

		self.started = True
		return self._cycle_start()

	def Stop(self):
		self.started = False

	def HardStop(self):
		if self.started:
			self.Stop()
			raise _HardStop()
		
	#### Cycle ####
	def _cycle_start(self):
		try:
			log.info('Bot started!')
			while self.started:
				self._cycle()
		except _HardStop:
			log.info('Bot was hard-stopped')
			return
		except ConnectionError:
			log.warning('Connection error. Next iteration after 5 seconds')
			time.sleep(5)
			return self._cycle_start()
	
	def _cycle(self):
		self.longpoll.update()
		if self.longpoll.eventsCount == 0: return
		for event in self.longpoll.events:
			eventObj = event['object']
			eventType = event['type']

			if not eventType in Event:
				log.warning('Unknown event: ' + str(eventType))
				log.warning('Event was ignored')
				continue

			hName = '_event_' + Event._find_value_path(eventType)
			if hasattr(self, hName):
				getattr(self, hName)(eventObj)
				pass
	
	#### Handlers ####
	# !! Примечание !!
	# Данные хандлеры преднозначены только для поиска ID отправителя из события, если это возможно, и передачи самого события, вместе с объектом события в хандлер
	# Не добавляйте ничего в данную группу, используйте группу хандлеров из User api
	def _event_Message_New(self, obj: dict):
		sender = obj['message']['from_id']
		self.CallEventHandler('Message_New', obj, sender)

	def CallEventHandler(self, name: str, obj: dict, sender: str | int):
		if type(sender) != int:
			try: sender = int(sender)
			except:
				log.error('Failed parsing ID <' + str(sender) + '> to integer. Event <' + str(name) + '> aborted.')
				return

		if sender not in self.users:
			usr = User(sender, self.api)
			abortCreatingUser = self.OnNewUser(usr)
			if abortCreatingUser:
				log.info('Creating user with id <' + str(sender) + '> aborted by <OnNewUser> handler. Event <' + str(name) + '> aborted too.')
				return
			else:
				try:
					response = self.api.executeMethod('users.get', {'user_ids': sender})[0]
					usr.name = response['first_name']
					usr.surname = response['last_name']
					usr.initialized = True
					usr.last_event = time.time()
				except vk_api.InvalidVkApiResponse as e:
					log.error('Failed getting info abour user <' + str(sender) + '>')
					log.error('Response: ' + str(e.response))
					log.info('User will be created anyway')
				self.users[sender] = usr
				log.info('New user with id: <' + str(sender) + '>')
		usr = self.users[sender]
		hName = 'EventHandler_' + str(name)
		if hasattr(self, hName):
			getattr(self, hName)(obj, usr)
	
	############ User api ############
	# Ниже, представленно так называемое 'user api'
	# Данное api необходимо для более лёгкой разработки и дополнения бота
	# Более подробную информацию о работе api вы можете узнать у издателя, либо просмотрев код выше

	#### Event Handlers ####
	def OnNewUser(self, usr: User) -> True | False:
		"""Вызывается при создании нового пользователя. Принимает объект ЕЩЕ НЕ СОЗДАННОГО пользователя.
		Если возвращает `True`, то пользователь НЕ БУДЕТ СОЗДАН, если `False`, то пользователь будет создан.
		Вы можете создать свой сценарий создания нового пользователя в этой функции, либо просто использовать её как хук."""

		usr.SendMessage(message="You're registred")
		pass

	#### Longpoll Handlers ###
	def EventHandler_Message_New(self, obj: dict, usr: User):
		usr.SendMessage(message='Received')
		pass