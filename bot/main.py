import logging

log = logging.getLogger('scamLife.bot')

from . import vk_api
from .enums import *
from .keyboard import *
from .users import User, UsersDB
from .database import Database
from .messages import txt

import sys
import time
import traceback
import re

class _HardStop(Exception): pass

class Bot(object):
	def __init__(self, apiSession: vk_api.ApiSession, groupID: int, db: Database) -> None:
		self.api = apiSession
		self.group_id = groupID

		self.longpoll = vk_api.LongPollServer(self.api.token, self.group_id, self.api)

		self.usersCached = {}

		self.dbRaw = db
		self.users = UsersDB(self.dbRaw, self.api)

		self.secret = time.time()

		self.started = False
	
	def Start(self):
		log.debug('Starting...')

		self.started = True
		log.info('Bot started!')
		return self._cycle_start()

	def Stop(self):
		log.info('Stopping...')
		log.info('Uncaching all users...')
		usersToDel = []
		for k, usr in self.usersCached.items():
			usr: User
			self.users.RemoveUserByID(usr.id)
			self.users.NewUser(usr)
			usersToDel.append(k)
		for k in usersToDel:
			log.info('Uncaching user <' + str(k) + '>...')
			del self.usersCached[k]
		log.info('Bot was stopped.')
		self.started = False

	def HardStop(self):
		if self.started:
			self.Stop()
			raise _HardStop()
		
	#### Cycle ####
	def _cycle_start(self):
		try:
			while self.started:
				self._cycle()
				self._check_users()
			if not self.started: return
		except _HardStop:
			log.info('Bot was hard-stopped')
			return
		except ConnectionError:
			log.warning('Connection error.')
			f_tb = ''
			for line in traceback.format_exception(*sys.exc_info()):
				f_tb = f_tb + line	
			log.warning(f_tb)
		except KeyboardInterrupt:
			self.Stop()
			return
		except:
			log.warning('Unhandled error in bot cycle.')
			f_tb = ''
			for line in traceback.format_exception(*sys.exc_info()):
				f_tb = f_tb + line
			log.warning(f_tb)
		log.info('Next iteration after 5 second')
		time.sleep(5)
		self._cycle_start()

	def _check_users(self):
		usersToDel = []
		for k, usr in self.usersCached.items():
			usr: User
			log.debug('checking usr <' + str(usr.id) + '> for event. Last event: ' + str(time.time() - usr.lastEvent))

			if (time.time() - usr.lastEvent) > 600:
				self.users.RemoveUserByID(usr.id)
				self.users.NewUser(usr)
				usersToDel.append(k)
		for k in usersToDel:
			log.info('Uncaching user <' + str(k) + '>...')
			del self.usersCached[k]
	
	def _cycle(self):
		self.longpoll.update()
		if self.longpoll.eventsCount == 0: return
		for event in self.longpoll.events:
			try:
				eventObj = event['object']
				eventType = event['type']

				if not eventType in Event:
					log.warning('Unknown event: ' + str(eventType))
					log.warning('Event was ignored')
					continue

				hName = '_event_' + Event._find_value_path(eventType)
				if hasattr(self, hName):
					getattr(self, hName)(eventObj)
			except vk_api.InvalidVkApiResponse as e:
				log.warning('Invalid vk_api response while handling event <' + str(event['type'] + '>'))
				log.warning('Response: ' + str(e.response))
				log.info('Event was skipped')
				continue
			except:
				log.warning('Error while handling event! Event Object: ' + str(event))
				f_tb = ''
				for line in traceback.format_exception(*sys.exc_info()):
					f_tb = f_tb + line
				log.warning(f_tb)
				log.info('Event was skipped')
				continue
	
	#### Handlers ####
	# !! Примечание !!
	# Данные хандлеры преднозначены только для поиска ID отправителя из события, не делайте там никакой дополнительной логики
	# Используйте User api
	def _event_Message_New(self, obj: dict):
		sender = obj['message']['from_id']
		self.CallEventHandler('Message_New', obj, sender)
	
	def _event_CallbackButton_Press(self, obj: dict):
		sender = obj['user_id']
		self.CallEventHandler('CallbackButton_Press', obj, sender)

	def CallEventHandler(self, name: str, obj: dict, sender: str | int):
		if type(sender) != int:
			try: sender = int(sender)
			except:
				log.error('Failed parsing ID <' + str(sender) + '> to integer. Event <' + str(name) + '> aborted.')
				return

		if sender not in self.usersCached:
			usr = self.users.GetUserByVkID(sender)
			if usr == None:
				usr = User(sender, self.api)
				abortCreatingUser = self.OnNewUser(usr)
				if abortCreatingUser:
					log.info('Creating user with id <' + str(sender) + '> aborted by <OnNewUser> handler. Event <' + str(name) + '> aborted too.')
					return
				else:
					self.usersCached[sender] = usr
					log.info('New user with id: <' + str(sender) + '>')
			else:
				log.info('Caching user <' + str(sender) + '>...')
				self.usersCached[sender] = usr
		usr: User = self.usersCached[sender]
		if not usr.infoInitialized:
			try:
				response = self.api.executeMethod('users.get', {'user_ids': sender})[0]
				usr.info['userName'] = response['first_name']
				usr.info['userSurname'] = response['last_name']
				usr.info['infoInitialized'] = True
			except vk_api.InvalidVkApiResponse as e:
				log.error('Failed initializing info abour user <' + str(sender) + '>')
				log.error('API Response: ' + str(e.response))

		usr.info['lastEvent'] = time.time()
		hName = 'EventHandler_' + str(name)
		if hasattr(self, hName):
			getattr(self, hName)(obj, usr)
	
	############ User api ############
	# Ниже, представленно так называемое 'user api'
	# Данное api необходимо для более лёгкой разработки и дополнения бота
	# Более подробную информацию о работе api вы можете узнать у издателя, либо просмотрев код выше

	#### Utils and etc. ####
	def ProcessAdminCMD(self, text: str, usr: User):
		if re.match(r'dbset \d+:.*=.*', text) != None:
			m = re.match(r'dbset (\d+):(.*)=(.*)', text)
			id = m.group(1)
			key = m.group(2)
			value = m.group(3)
			try: value = int(value)
			except: pass
			self.users.UpdateUserInfo(id, key, value)
			usr.SendMessage(message='+')
		elif re.match(r'uinfoset \d+:.*=.*', text) != None:
			m = re.match(r'uinfoset (\d+):(.*)=(.*)', text)
			id = m.group(1)
			key = m.group(2)
			value = m.group(3)
			try: value = int(value)
			except: pass
			if id not in self.usersCached:
				usr.SendMessage(message='user not cached')
				return
			_usr: User = self.usersCached[id]
			_usr.SendMessage(message='Администратор установил вам параметр "' + str(key) + '" на ' + str(value))
			_usr.info[key] = value
			self.usersCached[id] = _usr
			usr.SendMessage(message='+')
		elif re.match(r'cacheuser \d+', text) != None:
			id = re.match(r'cacheuser (\d+)', text).group(1)
			if id in self.usersCached:
				usr.SendMessage(message='user already cached')
				return
			_usr = self.users.GetUserByID(id)
			if _usr == None:
				usr.SendMessage(message='invalid user')
				return
			_usr.info['lastEvent'] = time.time()
			self.usersCached[id] = _usr
			usr.SendMessage(message='+')
			return
		elif re.match(r'uncacheuser \d+', text) != None:
			id = re.match(r'uncacheuser (\d+)', text).group(1)
			if id not in self.usersCached:
				usr.SendMessage(message='user not cached')
				return
			log.info('Uncaching user <' + str(id) + '>...')
			del self.usersCached[id]
			usr.SendMessage(message='+')
		elif re.match(r'botstop.*', text) != None:
			if re.match(r'botstop ' + str(self.secret), text) != None:
				usr.SendMessage(message='stopping...')
				self.Stop()
				return
			else:
				usr.SendMessage(message=str(self.secret))
				return
		else:
			usr.SendMessage(message='invalid command')
	
	def ShowMainMenu(self, usr: User, annStart: str = '', annEnd: str =''):
		usr.SendMessage(message=(annStart+'\n\n' if annStart != '' else '') +
										txt('GREETING') + ', {nickname}. у тебя на сбере ща {money} рублей'
		.format(**usr.info)
		+ '\n\n' + str(annEnd),
		keyboard=KB_MENU)
	
	def ShowSettings(self, usr: User):
		usr.SendMessage(message='настройъочки',
		keyboard=keyboard(KB_SETTINGS, snackbar_switch=usr.snackbarsInMsg))

	
	def ShowMenuByState(self, usr: User):
		s = usr.state
		if s == UserState.InMenu:
			self.ShowMainMenu(usr)
		elif s == UserState.InSettings:
			self.ShowMainMenu(usr)
		else:
			return False
		return True

	#### Event Handlers ####
	def OnNewUser(self, usr: User) -> True | False:
		"""Вызывается при создании нового пользователя. Принимает объект ЕЩЕ НЕ СОЗДАННОГО пользователя.
		Если возвращает `True`, то пользователь НЕ БУДЕТ СОЗДАН, если `False`, то пользователь будет создан.
		Вы можете создать свой сценарий создания нового пользователя в этой функции, либо просто использовать её как хук."""

		usr.SendMessage(message="registred. id=" + str(usr.id))
	
	#### Longpoll Handlers ###
	def EventHandler_Message_New(self, obj: dict, usr: User):
		text: str = obj['message']['text']

		if text.startswith('$') and usr.admin:
			text = text[1:]
			return self.ProcessAdminCMD(text, usr)
		
		if usr.state == UserState.Idle:
			if usr.registred:
				usr.SendMessage(message=txt('ERROR_RET_TO_MENU'))
				usr.info['state'] = UserState.InMenu
			else: 
				usr.SendMessage(message=txt('ENTER_NICKNAME'))
				usr.info['state'] = UserState.WaitForNickname
			return
		elif usr.state == UserState.WaitForNickname:
			usr.info['nickname'] = text
			usr.SendMessage(message=txt('YOUR_NICKNAME_NOW', nickname=text))
			usr.info['registred'] = True
			usr.info['state'] = UserState.InMenu
			return

		if not usr.registred:
			usr.info['state'] = UserState.Idle
			self.EventHandler_Message_New(obj, usr)

		if text == '!снекбар':
			usr.info['snackbarsInMsg'] = not usr.info['snackbarsInMsg']
			usr.SendMessage(message=(txt('SNACKBAR_IN_MSGS_ON') if usr.snackbarsInMsg else txt('SNACKBAR_IN_MSGS_OFF')))
			return
		elif text == '!обновить':
			updated = self.ShowMenuByState(usr)
			if not updated:
				usr.SendMessage(message='нечего обновлять(')
			return
		
		if usr.state == UserState.InMenu:
			self.ShowMainMenu(usr, annStart='Используй кнопки >:(')
			return
		usr.SendMessage(message='Используй кнопки! Если кнопки пропали, используй !обновить')
	
	def EventHandler_CallbackButton_Press(self, obj: dict, usr: User):
		def SendEmptyAnswer():
			self.api.executeMethod('messages.sendMessageEventAnswer', {
				'event_id': obj['event_id'],
				'user_id': obj['user_id'],
				'peer_id': usr.id,
				'event_data': ''
			})
		def SendSnackbar(text: str):
			if not (usr.flags & UserFlag.SnackbarAsked):
				usr.SendMessage(message=txt('SNACKBAR_IN_MSGS_ASK'))
				usr.info['flags'] = usr.info['flags'] | UserFlag.SnackbarAsked
			if usr.snackbarsInMsg:
				self.api.executeMethod('messages.send', {
					'peer_id': usr.id,
					'random_id': 0,
					'message': text
				})
			self.api.executeMethod('messages.sendMessageEventAnswer', {
				'event_id': obj['event_id'],
				'user_id': obj['user_id'],
				'peer_id': usr.id,
				'event_data': json.dumps({
					"type": "show_snackbar",
					"text": text
				})
			})

		payload = obj['payload']
		if 'ktype' not in payload or 'btype' not in payload:
			log.warning('Received invalid callback button. Object: ' + str(obj))
			return
		ktype = payload['ktype']
		btype = payload['btype']
		
		if btype == 'dummy':
			return SendSnackbar('Dummy Received in "' + str(ktype) + '"')
		
		if ktype == 'main_menu':
			if btype == 'reload':
				SendEmptyAnswer()
				self.ShowMainMenu(usr)
			elif btype == 'settings':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InSettings
				self.ShowSettings(usr)
		elif ktype == 'settings':
			if btype == 'reload':
				SendEmptyAnswer()
				self.ShowSettings(usr)
			elif btype == 'snackbar_switch':
				usr.info['snackbarsInMsg'] = not usr.info['snackbarsInMsg']
				SendSnackbar('Уведомления в сообщениях ' + ('включены' if usr.snackbarsInMsg else 'выключены'))
				self.ShowSettings()
			elif btype == 'return':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InMenu
				self.ShowMainMenu(usr)