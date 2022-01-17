class Item(object):
	def __new__(cls, uid: str, name: str) -> dict:
		return {'id': uid, 'name': name}