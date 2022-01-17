from .database import Database, Any

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

			'maxScore2048': 0
		}

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
		return self._util_CreateUserFromDict(r)
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
