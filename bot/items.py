class Item(object):
	def __new__(cls, uid: str, name: str) -> dict:
		return {'id': uid, 'name': name}

ITEM_NAMES = {
	'iphone6s': 'IPhone 6s',
	'xiaominote9': 'Xiaomi Note 9',
	'clock0': 'Старые часы',
	'clock1': 'Обычные часы',
	'clock2': 'Современные часы',
	'clock3': 'Дорогие Наручные часы',
	'clockmax': 'Наручные Часы с бриллиантами',
	
}

def GetItemName(id: str):
	if id in ITEM_NAMES:
		return ITEM_NAMES[id]
	return 'Неизвестно: ' + str(id)