from .database import Database, Any
from .items import *

class User(object):
	def __init__(self, id: int, api):
		self.id = id
		
		self.api = api

		self.game2048 = None

		self.info = {
			'id': self.id,

			'registred': False,
			'nickname': '',

			'state': 0,

			'lastEvent': 0,

			'userName': '',
			'userSurname': '',

			'money': 0,
			'euro': 0,
			'admin': False,

			'infoInitialized': False,

			'snackbarsInMsg': False,
			'flags': 0,

			'scam_adName': '',
			'scam_adDesc': '',
			'scam_adCreate': '',
			'scam_adEnd': '',

			'maxScore2048': 0,

			'promo': ''
		}

		self.inventory: list[Item] = []
		self.lists: dict[str, list] = {}

		def __setattr__(self, __name: str, __value: Any) -> None:
			if __name in self.info: self.info[__name] = __value
			else: super().__setattr__(__name, __value)
		self.__setattr__ = __setattr__
	
	def SendMessage(self, **kwargs):
		if 'random_id' not in kwargs:
			kwargs['random_id'] = 0
		kwargs['peer_id'] = self.id

		return self.api.executeMethod('messages.send', kwargs)

	def __getattr__(self, __name: str) -> Any:
		if __name in self.info: return self.info[__name]
		else: super().__getattribute__(__name)

class UsersDB(object):
	def __init__(self, db: Database, api) -> None:
		self.db = db
		self.api = api

	def _util_CreateUserFromDict(self, r: dict) -> User:
		usr = User(r['id'], self.api)
		for k, v in r.items():
			usr.info[k] = v
		return usr
	
	def _utils_dictToSqlPs(self, d: dict) -> list:
		lst = []
		i = 0
		for row in self.db.rows:
			lst.append(d[row.name])
			i += 1
		return lst

	def GetUserByID(self, id: int) -> None | User:
		r = self.db.GetRow(id)
		if r == None: return None
		usr = self._util_CreateUserFromDict(r)
		r = self.db.Execute(f'SELECT * FROM uInventory_{usr.id}')
		for item in r:
			usr.inventory.append(Item(item[1], GetItemName(item[1])))
		r = self.db.Execute(f'SELECT * FROM uLists_{usr.id}')
		for item in r:
			usr.lists['promosEntered'][item[0]] = item[1]
		return usr
	def GetUserByVkID(self, id: int) -> None | User:
		return self.GetUserByID(id)
	def GetUsersByProperty(self, propertyName: str, propertyValue: Any) -> list[User] | None:
		res = self.db.GetRowByCol(propertyName, propertyValue)
		if res.__len__() == 0: return None
		lst = []
		for r in res:
			lst.append(self._util_CreateUserFromDict(r))
		return lst
	
	def GetAll(self) -> list[User]:
		res = self.db.GetAll()
		lst = []
		for r in res:
			lst.append(self._util_CreateUserFromDict(r))
		return lst
	
	def RemoveUserByID(self, id: int):
		self.db.RemoveRow(id)
	def RemoveUserByVkID(self, id: int):
		self.RemoveUserByID(id)

	def UpdateUserInfo(self, id: int, pName: str, pValue: Any):
		self.db.UpdateRow(id, pName, pValue)
	
	def NewUser(self, usr: User):
		self.db.InsertRow(*self._utils_dictToSqlPs(usr.info))
		self.db.Execute(f'''CREATE TABLE IF NOT EXISTS uInventory_{usr.id} (
			slotId tinyint UNIQUE,
			itemId nvarchar(42),
			itemFlags bigint,
			PRIMARY KEY (slotId)
		)''')
		self.db.Execute(f'''CREATE TABLE IF NOT EXISTS uLists_{usr.id} (
			itemIndex bigint UNIQUE,
			promosEntered nvarchar(12),
			PRIMARY KEY (itemIndex)
		)''')
		i = 0
		for item in usr.inventory:
			item: Item
			self.db.InsertRow(i, item['id'], 0, target_table=f'uInventory_{usr.id}')
			i += 1
		maxI = 0
		for colName, col in usr.lists.items():
			i = 0
			for item in col:
				if i < maxI:
					self.db.InsertRow(i, item, cols=['itemIndex', colName], target_table=f'uLists_{usr.id}')
					maxI = i
				else:
					self.db.UpdateRow(i, colName, item, target_table=f'uLists_{usr.id}')
				i += 1
