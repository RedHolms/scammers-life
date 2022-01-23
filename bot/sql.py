from .database import Database, Any
import sqlite3

class SQLfield(object):
	def __init__(self, name: str, type: str, flags: list[str] = []) -> None:
		self.name = name
		self.type = type
		self.flags = flags

class SQL(Database):
	def __init__(self, dbPath: str, rows: list[SQLfield], primaryKey: str = 'id', mainTable: str = 'main') -> None:
		self.conn = sqlite3.connect(dbPath)
		self.cur = self.conn.cursor()
		self.mainTable = mainTable
		self.primaryKey = primaryKey
		self.rows = rows

		s = \
		f"CREATE TABLE IF NOT EXISTS {self.mainTable} (\n" + \
		f"	{self._util_unpackToStr([f.name + ' ' + f.type + ' ' + self._util_unpackToStr(f.flags, False, True) for f in rows], False)},\n" + \
		f"	PRIMARY KEY ({self.primaryKey})\n" + \
		f");"

		self.cur.execute(s)

	# Utils
	def _util_formatSqlVal(self, v: Any) -> str:
		return (("'" + v + "'") if type(v) == str else str(int(v)) if type(v) == int else str(v))

	def _util_unpackToStr(self, lst: list, formatStrings: bool = True, removeComma: bool = False):
		retS = ""
		i = 1
		for v in lst:
			if formatStrings:
				retS = retS + self._util_formatSqlVal(v)
			else:
				retS = retS + str(v)
			if i < lst.__len__():
				retS = retS + (', ' if not removeComma else ' ')
			i += 1
		return retS

	def _util_sqlResToDict(self, sqlRes: tuple[Any]):
		i = 0
		dct = {}
		for v in sqlRes:
			_v = self.rows[i]
			if _v.type == 'bit': v = bool(v)
			dct[self.rows[i].name] = v
			i += 1
		return dct
	
	def _utils_dictToSqlPs(self, d: dict) -> list:
		lst = []
		i = 0
		for row in self.rows:
			lst.append(d[row.name])
			i += 1
		return lst

	# Implemintation

	def GetRowByCol(self, colName: str, colValue: Any, target_table: str = None) -> list[dict[str, Any]]:
		"""return (SELECT * FROM $target_table WHERE $colName = $colValue)"""
		if target_table == None: target_table = self.mainTable
		self.cur.execute(f'SELECT * FROM {target_table} WHERE {colName} = {colValue};')
		return [self._util_sqlResToDict(v) for v in self.cur.fetchall()]
	
	def GetRow(self, rowI: int, target_table: str = None) -> dict[str, Any]:
		"""return (SELECT * FROM $target_table WHERE $self.primaryKey = $rowI)[0]"""
		if target_table == None: target_table = self.mainTable
		self.cur.execute(f'SELECT * FROM {target_table} WHERE {self.primaryKey} = {rowI};')
		r = self.cur.fetchall()
		if r.__len__() == 0: return None
		else: return self._util_sqlResToDict(r[0])

	def InsertRow(self, *args, cols: list=[], target_table: str = None):
		"""IF cols != [] THEN
			INSERT INTO $target_table (*$cols) VALUES (*$args)
		ELSE
			INSERT INTO $target_table VALUES (*$args)"""
		if target_table == None: target_table = self.mainTable
		if cols == []:
			self.cur.execute(f'INSERT INTO {target_table} VALUES ({self._util_unpackToStr(args)});')
		else:
			self.cur.execute(f'INSERT INTO {target_table} ({self._util_unpackToStr(cols, False)}) VALUES ({self._util_unpackToStr(args)});')
		self.conn.commit()

	def UpdateRow(self, rowI: int, colName: str, colValue: Any, target_table: str = None):
		if target_table == None: target_table = self.mainTable
		print(f'UPDATE {target_table} SET {colName} = {self._util_formatSqlVal(colValue)} WHERE {self.primaryKey} = {rowI}')
		self.cur.execute(f'UPDATE {target_table} SET {colName} = {self._util_formatSqlVal(colValue)} WHERE {self.primaryKey} = {rowI}')
	
	def RemoveRow(self, rowI: int, target_table: str = None):
		"""DELETE FROM $target_table WHERE $self.primaryKey = $rowI"""
		if target_table == None: target_table = self.mainTable
		self.cur.execute(f'DELETE FROM {target_table} WHERE {self.primaryKey} = {rowI}')
		self.conn.commit()
	
	def GetAll(self, target_table: str = None):
		self.cur.execute(f'SELECT * FROM {target_table}')
		return self.cur.fetchall()
	
	def Execute(self, code: str) -> list:
		self.cur.execute(code)
		return self.cur.fetchall()
	
	def Close(self):
		self.conn.close()