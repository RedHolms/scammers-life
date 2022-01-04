import logging
log = logging.getLogger('scamLife.bot.main')

from . import vk_api
from .enums import *


class UserEnviroment(object):
	def __init__(self, **kwargs) -> None:
		for k, v in kwargs.items():
			setattr(self, k, v)

default_uEnv = UserEnviroment(
	registred=False,
	nickname='',
	id = 0,
	name = '',
	surname = '',
	fullname = '',
	state=UserState.Idle
)

class Bot(object):
	def __init__(self, apiSession: vk_api.ApiSession, groupID: int) -> None:
		self.api = apiSession
		self.groupID = groupID

		self.uEnv = {}

	# Utils
	def sendMessage(self, peer: int, text: str):
		try:
			response = self.api.executeMethod('messages.send', {'random_id':0, 'peer_id': peer, 'message': text})
		except vk_api.InvalidVkApiResponse as e:
			log.warning('Error while trying to send message[1]!')
			log.warning('Peer: ' + str(peer))
			log.warning('Message text: ' + str(text))
			log.warning('Api Response: ' + str(e.response))
			return False, e.response
		return True, response

	# Main
	
	def start(self):
		log.debug('Setting up longpoll...')

		self.longpoll = vk_api.LongPollServer(self.api.token, self.groupID, self.api, 25)

		log.info('Bot started!')
		while True:
			self.longpoll.update()

			if self.longpoll.eventsCount == 0: continue
			for event in self.longpoll.events:
				eventType = event['type']
				eventObject = event['object']

				if not eventType in Event:
					log.warning('Unknown event <' + str(eventType) + '>. Ignored.')
					continue
				
				handlerName = 'EventHandler_' + str(Event._find_value_path(eventType))
				if hasattr(self, handlerName):
					getattr(self, handlerName)(eventObject)
	
	# Event Handlers
	# Что-бы добавить новый хандлер евента, достаточно добавить в класс метод, с именем формата:
	# EventHandler_EVENTPATH, где:
	# EVENTPATH - 'Путь' к евенту(см. фалй enums.py)
	# 
	# Формат параметров хандлера:
	# (self: Bot, eventObject: dict)
	# self - Объект бота
	# eventObject - Объект евента
				
	def EventHandler_Message_New(self, eventObject: dict):
		messageObject = eventObject['message']
		msgText = messageObject['text']
		msgFrom = messageObject['from_id']
		msgPeer = messageObject['peer_id']
		msgId = messageObject['id']

		def answer(text):
			return self.sendMessage(msgFrom, text)
		
		if not msgFrom in self.uEnv:
			self.uEnv[msgFrom] = default_uEnv
			uEnv = self.uEnv[msgFrom]

			uEnv.id = msgFrom

			response = self.api.executeMethod('users.get', {'user_ids': msgFrom}, safeMode=True)
			if 'error' in response:
				log.warning('Error while trying to get user info of id: ' + str(msgFrom))
				answer('Ошибка! Попробуйте позже')
				return

			answer('Введите имя пользователя:')
			self.uEnv[msgFrom].state = UserState.WaitForNickname
		else:
			uEnv = self.uEnv[msgFrom]
			if uEnv.state == UserState.InMenu:
				answer(uEnv.nickname + ', вы находитесь в меню')
			elif uEnv.state == UserState.WaitForNickname:
				uEnv.nickname = msgText
				answer('Теперь ваше имя: ' + str(uEnv.nickname))
				uEnv.state = UserState.InMenu