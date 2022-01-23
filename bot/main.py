import logging
log = logging.getLogger('scamLife.bot')

from . import vk_api
from .enums import *
from .keyboard import *
from .shop import *
from .games import *
from .thief_manager import *
from .items import *
from .promo import *
from .users import User, UsersDB
from .database import Database
from .messages import txt
from .files import FileLoader

import sys
import time
import traceback
import re
import random
import math

class _HardStop(Exception): pass

class Bot(object):
	def __init__(self, apiSession: vk_api.ApiSession, groupID: int, db: Database, img_album: int) -> None:
		self.api = apiSession
		self.group_id = groupID

		self.longpoll = vk_api.LongPollServer(self.api.token, self.group_id, self.api)

		self.usersCached = {}

		self.dbRaw = db
		self.users = UsersDB(self.dbRaw, self.api)

		self.secret = time.time()

		self.img_album = img_album
		
		self.fl = FileLoader(self.api, self.group_id, img_album)
		self.pm = PromoManager(self)

		self.started = False

	def CacheUser(self, id: int) -> User | None:
		if id not in self.usersCached:
			usr = self.users.GetUserByVkID(id)
			if usr == None:
				return None
			else:
				log.info('Caching user <' + str(id) + '>...')
				self.usersCached[id] = usr
		return self.usersCached[id]
	
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
		for k, usr in self.usersCached.items():
			usr: User
			if usr.flags & UserFlag.ScamWaiting:
				if (usr.scam_adCreate + usr.scam_adEnd) <= time.time():
					usr.info['flags'] = usr.info['flags'] & (~UserFlag.ScamWaiting)
					random.seed(time.time())
					c = round(random.random() * 5 + 5)
					usr.SendMessage(message=f'✅ поздавляю! вы заскамили мамонта на авито! на сбер было зачисленно {c} рублей')
					usr.info['money'] += c

		usersToDel = []
		for k, usr in self.usersCached.items():
			usr: User
			log.debug('checking usr <' + str(usr.id) + '> for event. Last event: ' + str(time.time() - usr.lastEvent))

			if (time.time() - usr.lastEvent) > 600 and not (usr.flags & UserFlag.ScamWaiting):
				if usr.flags & UserFlag.Gaming:
					usr.SendMessage(message='игра была завершена из-за бездействия(награды не будет)')
					usr.game2048 = None
					usr.info['state'] = UserState.InGames
					usr.info['flags'] &= ~UserFlag.Gaming
					self.ShowGames(usr)

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
				f_tb = ''
				for line in traceback.format_exception(*sys.exc_info()):
					f_tb = f_tb + line
				log.warning(f_tb)
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
		if obj['message']['peer_id'] >= 2000000000: return
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

		if usr.state == UserState.Idle:
			if usr.registred:
				usr.SendMessage(message=txt('ERROR_RET_TO_MENU'))
				usr.info['state'] = UserState.InMenu
			else: 
				usr.SendMessage(message=txt('ENTER_NICKNAME'))
				usr.info['state'] = UserState.WaitForNickname
			return

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
		elif re.match(r'invadd .+', text) != None:
			m = re.match(r'invadd (.+)', text)
			item = m.group(1)
			usr.inventory.append(Item(item, GetItemName(item)))
		elif re.match(r'botstop.*', text) != None:
			if re.match(r'botstop ' + str(self.secret), text) != None:
				usr.SendMessage(message='stopping...')
				self.Stop()
			else:
				usr.SendMessage(message=str(self.secret))
			return
		elif re.match(r'money \d+', text) != None:
			m = re.match(r'money (\d+)', text)
			money = m.group(1)
			usr.info['money'] += int(money)
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

	def ShowShop(self, usr: User):
		_templ = json.dumps({
			'type': 'carousel',
			'elements': [
				{
					'title': item['name'],
					'description': str(item['price']) + ' евро',
					'photo_id': self.fl.LoadImage(item['img']),
					'action': {"type": "open_photo"},
					'buttons': [
						{
							'action': {
								'type': 'callback',
								'label': 'купить',
								'payload': {
									'ktype': 'shop',
									'btype': 'buy',
									'payload': {
										'item': item['item']
									}
								}
							},
							'color': 'primary'
						},
						{
							'action': {
								'type': 'callback',
								'label': 'подробнее',
								'payload': {
									'ktype': 'shop',
									'btype': 'about',
									'payload': {
										'item': item['item']
									}
								}
							},
							'color': 'primary'
						}
					]
				}
			for item in SHOP_ITEMS]
		})
		usr.SendMessage(message='дарова, тут магаз короче, я не придумал чё еще сюда можно написать так что пускай будет так', keyboard=KB_SHOP)
		usr.SendMessage(template=_templ, message='вещъчьки')
	
	def ShowVipshop(self, usr: User):
		usr.SendMessage(message='в сбере можно обменять евро на рубли, тут у нас не россия, поэтому курс 1 евро = 10 рублей.\nвведите кол-во евро, сколько хочешь обменять:', keyboard=KB_VIPSHOP)
	
	def ShowDonate(self, usr: User):
		usr.SendMessage(message='донатек', keyboard=KB_DONATE)

	def ShowWorksList(self, usr: User):
		usr.SendMessage(message="вот список работ, завода не будет, там только твой батя", keyboard=KB_WORKSLIST)

	def ShowWorkMenu_Scam(self, usr: User):
		usr.SendMessage(message="решил поскамить мамонтов на авито? отлично, размещай объявление и мамонты сами прибегут!", keyboard=KB_WORKMENU_SCAM)

	def ShowWorkMenu_Fishing(self, usr: User):
		usr.SendMessage(message=".")
	
	def ShowWorkMenu_Thief(self, usr: User):
		_templ = json.dumps({
			'type': 'carousel',
			'elements': [
				{
					'title': item['name'],
					'description': 'Сложность: ' + str(item['difficult_rus']),
					'photo_id': self.fl.LoadImage(item['thumbnail']),
					'action': {"type": "open_photo"},
					'buttons': [
						{
							'action': {
								'type': 'callback',
								'label': 'грабануть',
								'payload': {
									'ktype': 'thief_с',
									'btype': 'start',
									'payload': {
										'id': item['id']
									}
								}
							},
							'color': 'primary'
						},
						{
							'action': {
								'type': 'callback',
								'label': 'возможный дроп',
								'payload': {
									'ktype': 'thief_с',
									'btype': 'drop',
									'payload': {
										'id': item['id'],
										'drop': item['drop'],
										'house_name': item['name']
									}
								}
							},
							'color': 'primary'
						}
					]
				}
			for item in RandomThiefHouses()]
		})
		usr.SendMessage(message='решил грабануть кого-то значит. учти, если тебя поймают за жопу - в тюрьму, либо штраф', keyboard=KB_WORKMENU_THIEF)
		usr.SendMessage(message='выбирай, какой дом пойдёшь грабить', template=_templ)

	def ShowCasino(self, usr: User):
		usr.SendMessage(message='тут казиныч', keyboard=KB_CASINO)

	def ShowGames(self, usr: User):
		usr.SendMessage(message='тут игры где ты можешь заработать', keyboard=KB_GAMES)

	def ShowGameMenu_2048(self, usr: User):
		usr.SendMessage(message=f'игра тупа 2048. твой рекорд {usr.maxScore2048} очков', keyboard=KB_GAMEMENU_2048)
	
	def ShowPromos(self, usr: User):
		usr.SendMessage(message='введи промокод', keyboard=(KB_PROMOS_H if self.pm.IsUserHasPromo() != None else KB_PROMOS))

	
	def ShowMenuByState(self, usr: User):
		s = usr.state
		if s == UserState.InMenu:
			self.ShowMainMenu(usr)
		elif s == UserState.InSettings:
			self.ShowSettings(usr)
		elif s == UserState.InShop:
			self.ShowShop(usr)
		elif s == UserState.InVipshop:
			self.ShowVipshop(usr)
		elif s == UserState.InDonate:
			self.ShowDonate(usr)
		elif s == UserState.InWorksList:
			self.ShowWorksList(usr)
		elif s == UserState.InWorkMenu_Fishing:
			self.ShowWorkMenu_Fishing(usr)
		elif s == UserState.InWorkMenu_Scam:
			self.ShowWorkMenu_Scam(usr)
		elif s == UserState.InWorkMenu_Thief:
			self.ShowWorkMenu_Thief(usr)
		elif s == UserState.InCasino:
			self.ShowCasino(usr)
		elif s == UserState.InGames:
			self.ShowGames(usr)
		elif s == UserState.InGameMenu_2048:
			self.ShowGameMenu_2048(usr)
		elif s == UserState.InPromos:
			self.ShowPromos(usr)
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
	##########################
	def EventHandler_Message_New(self, obj: dict, usr: User):
		text: str = obj['message']['text']

		if text.startswith('$') and usr.admin:
			text = text[1:]
			return self.ProcessAdminCMD(text, usr)
		
		elif usr.state == UserState.WaitForNickname:
			if text.__len__() > 20:
				usr.SendMessage('ты чо, такое хер запомнишь, не больше 20 букав')
				return
			usr.info['nickname'] = text
			usr.SendMessage(message=txt('YOUR_NICKNAME_NOW', nickname=text))
			usr.info['registred'] = True
			usr.info['state'] = UserState.InMenu
			self.ShowMainMenu(usr)
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
		elif text == 'инвентарь':
			if usr.inventory.__len__() == 0:
				msg = 'ты бомж у тебя ничего нету'
			else:
				msg = 'твой инвентарь:\n\n'
				for item in usr.inventory:
					msg += item['name'] + '\n'
			usr.SendMessage(message=msg)
			return
		
		if usr.state == UserState.InMenu:
			self.ShowMainMenu(usr, annStart='Используй кнопки >:(')
			return
		elif usr.state == UserState.InVipshop:
			try:
				c = int(text)
			except:
				usr.SendMessage(message='это не число, что бы вернуться используй кнопки, если кнопки пропали введи !обновить')
			else:
				if c < 0:
					usr.SendMessage(message='в долг не даём')
					return
				if usr.euro < c:
					usr.SendMessage(message='у тебя нету столько, у тебя ' + str(usr.euro))
					return
				usr.info['euro'] -= c
				usr.info['money'] += c * 10
				usr.SendMessage(message=f'✅ вам было зачисленно {c * 10} рублей, у вас осталось {usr.euro} евро')
				self.ShowVipshop(usr)
			return
		elif usr.state == UserState.Scam_WaitForAdName:
			if text == '!назад':
				usr.info['state'] = UserState.InMenu
				self.ShowMainMenu(usr)
				return
			
			if text.__len__() > 32:
				usr.SendMessage(message='слишком длинное, не больше 32 букав')
				return
			usr.info['scam_adName'] = text
			usr.info['state'] = UserState.Scam_WaitForAdDesc
			usr.SendMessage(message='теперь описание')
			return
		elif usr.state == UserState.Scam_WaitForAdDesc:
			if text == '!назад':
				usr.info['state'] = UserState.InMenu
				self.ShowMainMenu(usr)
				return

			if text.__len__() > 92:
				usr.SendMessage(message='слишком длинное, не больше 92 букав')
				return
			usr.info['scam_adName'] = text
			usr.info['state'] = UserState.InWorkMenu_Scam
			usr.info['flags'] = usr.info['flags'] | UserFlag.ScamWaiting
			usr.info['scam_adCreate'] = time.time()
			random.seed(time.time())
			usr.info['scam_adEnd'] = ((random.random() * 1800) + 1800)
			usr.SendMessage(message='объявление было размещено, жди, пока какой-нибудь мамонт заскамится')
			self.ShowWorkMenu_Scam(usr)
			return
		elif usr.state == UserState.InPromos:
			if text in usr.lists['promosEntered']:
				usr.SendMessage(message='ты уже вводил этот промик')
				return
			state = self.pm.ActivatePromo(text, usr)
			if state == 1:
				usr.SendMessage(message='ошибка, промокод уже недействителен, или не существует')
			elif state == 2:
				usr.SendMessage(message='ты не можешь ввести свой же промик')
			elif state != 0:
				usr.SendMessage(message='ошибка при вводе промика, обратись в поддержку. код ошибки: ' + str(state))
			return
		elif usr.state == UserState.WaitForPromo:
			if usr.money < 10000:
				usr.SendMessage(message='у тебя недостаточно рублей. для создания промика надо 10к рублей')
				return
			state = self.pm.IsPromoCodeValid(text)
			if state == 0:
				usr.SendMessage(message=f'ты точно хочешь сделать промо "{text}"? ты потратишь 10к', keyboard=keyboard(KBU_CONFIRM, confirm={'promo': text}))
				usr.info['state'] = UserState.PromoConfirm
			elif state == 1:
				usr.SendMessage(message='такой промик уже занят')
			elif state == 2:
				usr.SendMessage(message='промик слишком длинный/короткий')
			return
		usr.SendMessage(message='Используй кнопки! Если кнопки пропали, используй !обновить')
	
	def EventHandler_CallbackButton_Press(self, obj: dict, usr: User):
		if not usr.registred:
			return

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
		payload = payload['payload']
		
		if btype == 'dummy':
			return SendSnackbar('Dummy Received in "' + str(ktype) + '"')
		elif btype == 'return':
			if 'retTo' not in payload:
				SendEmptyAnswer()
				usr.info['state'] = UserState.InMenu
				self.ShowMainMenu(usr)
			else:
				rt = payload['retTo']
				SendEmptyAnswer()
				usr.info['state'] = getattr(UserState, 'In' + str(rt))
				getattr(self, 'Show' + str(rt))(usr)
			return
		elif btype == 'confirm':
			if usr.state == UserState.PromoConfirm:
				promo = payload['promo']
				usr.info['money'] -= 10000
				self.pm.NewPromo(promo, usr)
				self.pm.SavePromos()
				usr.info['state'] = UserState.InMenu
				self.ShowMainMenu(usr, annStart=f'теперь у тебя есть промик "{promo}"')
			return
		elif btype == 'decline':
			usr.info['state'] = UserState.InMenu
			self.ShowMainMenu(usr)
			return
		
		if ktype == 'main_menu':
			if btype == 'reload':
				SendEmptyAnswer()
				self.ShowMainMenu(usr)
			elif btype == 'settings':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InSettings
				self.ShowSettings(usr)
			elif btype == 'shop':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InShop
				self.ShowShop(usr)
			elif btype == 'vipshop':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InVipshop
				self.ShowVipshop(usr)
			elif btype == 'donate':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InDonate
				self.ShowDonate(usr)
			elif btype == 'works':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InWorksList
				self.ShowWorksList(usr)
			elif btype == 'casino':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InCasino
				self.ShowCasino(usr)
			elif btype == 'games':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InGames
				self.ShowGames(usr)
			elif btype == 'promos':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InPromos
				self.ShowPromos(usr)

		elif ktype == 'settings':
			if btype == 'reload':
				SendEmptyAnswer()
				self.ShowSettings(usr)
			elif btype == 'snackbar_switch':
				usr.info['snackbarsInMsg'] = not usr.info['snackbarsInMsg']
				SendSnackbar('Уведомления в сообщениях ' + ('включены' if usr.snackbarsInMsg else 'выключены'))
				self.ShowSettings(usr)
		

		elif ktype == 'shop':
			if btype == 'bank':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InVipshop
				self.ShowVipshop(usr)
		

		elif ktype == 'donate':
			SendEmptyAnswer()


		elif ktype == 'vipshop':
			if btype == 'donate':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InDonate
				self.ShowDonate(usr)

		
		elif ktype == 'workslist':
			if btype == 'work_scamavito':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InWorkMenu_Scam
				self.ShowWorkMenu_Scam(usr)
			elif btype == 'work_fishing':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InWorkMenu_Fishing
				self.ShowWorkMenu_Fishing(usr)
			elif btype == 'thief':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InWorkMenu_Thief
				self.ShowWorkMenu_Thief(usr)

		
		elif ktype == 'casino':
			if btype == 'onehandbandit':
				SendEmptyAnswer()
		
		
		elif ktype == 'games':
			if btype == '2048':
				SendEmptyAnswer()
				usr.info['state'] = UserState.InGameMenu_2048
				self.ShowGameMenu_2048(usr)


		elif ktype == 'gamemenu_2048':
			if btype == 'play':
				SendEmptyAnswer()
				usr.info['state'] = UserState.Gaming_2048
				usr.game2048 = Game2048()
				usr.game2048.Clear()
				usr.game2048.Random()
				usr.info['flags'] |= UserFlag.Gaming
				usr.SendMessage(message=f'игра началась! правила стандарные, обычная игра 2048. каждые 100 очков = 1 рубль. удачи в наборе очкой! :3', keyboard=usr.game2048.FormatKeyboard())
		

		elif ktype == 'game2048':
			if usr.game2048 == None:
				SendSnackbar('ааа чёза ты как тут это да быстра в меню вернулся да(ошибка, трай агаин)')
				usr.info['state'] = UserState.InMenu
				self.ShowMainMenu(usr)
				return
			
			if btype == 'block':
				SendEmptyAnswer()
			elif btype == 'move':
				SendEmptyAnswer()
				moved = usr.game2048.Move(payload['dir'])
				if moved:
					usr.game2048.Random()
					if not usr.game2048.IsMovesAvailable():
						c = math.floor(usr.game2048.points / 100)
						usr.SendMessage(message=f'🙁 больше нету доступных ходов, гаме овер! на сбер зачисленно {c} рублей')
						usr.info['maxScore2048'] = usr.game2048.points
						usr.info['money'] += c
						usr.info['state'] = UserState.InGameMenu_2048
						usr.info['flags'] &= ~UserFlag.Gaming
						usr.game2048 = None
						self.ShowGameMenu_2048(usr)
						return
					usr.SendMessage(message=f'ты набрал {usr.game2048.points} очков или {math.floor(usr.game2048.points / 100)} рублей', keyboard=usr.game2048.FormatKeyboard())
			elif btype == 'exit':
				SendEmptyAnswer()
				c = math.floor(usr.game2048.points / 100)
				usr.SendMessage(message=f'на сбер зачисленно {c} рублей')
				usr.info['maxScore2048'] = usr.game2048.points
				usr.info['money'] += c
				usr.info['state'] = UserState.InGameMenu_2048
				usr.info['flags'] &= ~UserFlag.Gaming
				usr.game2048 = None
				self.ShowGameMenu_2048(usr)

		
		elif ktype == 'workmenu_scam':
			if btype == 'make_ad':
				if usr.flags & UserFlag.ScamWaiting:
					usr.SendMessage(message='ты уже размещал объявление, жди, пока мамонты заскамятся')
					return
				SendEmptyAnswer()
				usr.info['state'] = UserState.Scam_WaitForAdName
				usr.SendMessage(message='введи название объявы, что бы вернутся напиши !назад', keyboard=KB_WORKMENU_SCAM_R)
		
		
		elif ktype == 'thief_с':
			if btype == 'start':
				SendEmptyAnswer()
				id = payload['start']
			elif btype == 'drop':
				SendEmptyAnswer()
				s = 'возможный дроп из "' + str(payload['house_name']) + '":\n\n'
				for item in payload['drop']:
					item: Item
					s += str(item['name']) + '\n'
				usr.SendMessage(message=s)
		

		elif ktype == 'promos':
			if btype == 'create':
				SendEmptyAnswer()
				usr.SendMessage(message=f'для создания промокода нужно 10000 рублеков. если ты готов, введи промокод\n\nна первом уровне промокод будет давать {PROMO_LVLS[1][0]} тому, кто ввёл, и {PROMO_LVLS[1][1]} владельцу(тебе)', keyboard=keyboard(KBU_RETURN, kwargs={'return': {'retTo': 'Promos'}}))
				usr.info['state'] = UserState.WaitForPromo
			elif btype == 'manage':
				SendEmptyAnswer()
				if not self.pm.IsUserHasPromo(usr.id):
					usr.SendMessage(message=f'ошибка, у тебя нету промика')
					self.ShowPromos(usr)
					return
				

		else:
			log.warning('Callback button in invalid keyboard: ' + str(ktype))