from abc import ABCMeta, abstractmethod
from typing import Any

class Database(metaclass=ABCMeta):
	# Абстрактный класс для работы с базой данных
	#
	# Интерфейс к базе данных ДОЛЖЕН предоставляться в стиле таблицы
	# Каждая строка, возвращаемая из метода, представляет именованный список, пар [COLUMN]: [VALUE]
	# Если значение = NULL, будет возвращен None
	#
	# !!! Данный класс не реализует работу с базой данных, а лишь предоставляет интерфейс для работы с ней
	#
	# Класс представляет не столько базу данных, сколько таблицу
	# Рекомендуется использовать с SQL
	#
	# Каждый метод имеет опциональный параметр target_table, по умолчанию равный self.mainTable (в списке параметров равен None)
	# !!! Класс, реализующий базу данных может изменять данный параметр
	@abstractmethod
	def GetRowByCol(self, colName: str, colValue: Any, target_table: str = None) -> list[dict[str, Any]]:
		"""return list of rows, where $colName = $colValue"""
	
	@abstractmethod
	def GetRow(self, rowI: int, target_table: str = None) -> dict[str, Any]:
		"""return row with id $rowI"""
	
	@abstractmethod
	def InsertRow(self, *args, cols: list=[], target_table: str = None):
		"""insert row with cols $*args"""
	
	@abstractmethod
	def RemoveRow(self, rowI: int, target_table: str = None):
		"""remove row with id = $rowI"""
	
	@abstractmethod
	def UpdateRow(self, rowI: int, colName: str, colValue: Any, target_table: str = None):
		"""set $colName of row with id = $rowI to $colValue"""

	@abstractmethod
	def GetAll(self):
		"""return list of all rows"""
	
	@abstractmethod
	def Execute(self, code: str) -> list:
		"""execute code"""
