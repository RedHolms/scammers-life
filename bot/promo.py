import logging
_log_promo = logging.getLogger('scamLife.bot.promo')

PROMOS_FILE_NAME = 'promos.json'
PROMOS_FILE = 'bot\\' + PROMOS_FILE_NAME

import json
from . import users

"""
Promo lvls:

-1: // Special System promo
	To Activater - 1000
	To Definer - 1
0: // System promo
	To Activater - 100
	To Definer - 1
1: // User promo lvl: 1
	To Activater - 100
	To Definer - 10
2: // User promo lvl: 2
	To Activater - 150
	To Definer - 10
3: // User promo lvl: 3
	To Activater - 250
	To Definer - 10
4: // User promo lvl: 4
	To Activater - 400
	To Definer - 20
"""
PROMO_LVLS = {
	-1: (1000, 1),
	0: (100, 1),
	1: (100, 10),
	2: (150, 10),
	3: (250, 10),
	4: (400, 20),
}

class PromoManager(object):
	def __init__(self, botObj) -> None:
		with open(PROMOS_FILE, 'r') as f:
			self.promos: list = json.load(f)["promos"]
			f.close()
		self.bot = botObj
	
	def IsPromoValid(self, code: str) -> bool:
		for promo in self.promos:
			if promo['code'] == code and (promo['activations_lost'] > 0 or promo['activations_list'] == -1):
				return True
		return False
	
	def GetPromo(self, code: str) -> dict:
		for promo in self.promos:
			if promo['code'] == code:
				return promo
		return None
	
	def ChangePromo(self, code: str, promoObj: dict) -> int:
		i = 0
		for promo in self.promos:
			if promo['code'] == code:
				self.promos[i] = promoObj
				return i
			i += 1
		
	def SavePromos(self):
		with open(PROMOS_FILE, 'w') as f:
			json.dump({'promos': self.promos}, f)
			f.close()

	def ActivatePromo(self, code: str, usr: users.User) -> int:
		if not self.IsPromoValid(code):
			return 1
		
		promo = self.GetPromo(code)
		promoLvl = promo['lvl']
		definer = promo['owner']

		if usr.id == definer:
			return 2

		toActivator, toDefiner = PROMO_LVLS[promoLvl]
		usr.info['money'] += toActivator
		usr.SendMessage(message=f'✅ промокод дал тебе {toActivator} рубликов')

		promo['activations_lost'] -= 1
		self.ChangePromo(code, promo)
		self.SavePromos()

		usr = self.bot.CacheUser(definer)
		if usr == None:
			_log_promo.warning(f'promo with invalid definer: promo={code}; definer={definer}')
		else:
			usr.info['money'] += toDefiner
			usr.SendMessage(message=f'✅ кто-то ввёл твой промокод. ты получил {toDefiner} рубликов')
		return 0

	def NewPromo(self, code: str, owner: users.User) -> int:
		self.promos.append({
			"code": code,
			"activations_lost": -1,
			"owner": owner.id,
			"lvl": 1
		})
		return self.promos.__len__() - 2
	
	def IsPromoCodeValid(self, code: str) -> int:
		if code.__len__() < 4 and code.__len__() > 12:
			return 2
		for promo in self.promos:
			if promo['code'] == code:
				return 1
		return 0

	def IsUserHasPromo(self, usr: int) -> dict | None:
		for promo in self.promos:
			if promo['definer'] == usr:
				return promo
		return None

