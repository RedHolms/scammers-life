msgs = {
	'ENTER_NICKNAME': "enter username",
	'ERROR_RET_TO_MENU': "Произошла ошибка. Вы были возвращены в меню",
	'ERROR_TRY_AGAIN': "Произошла ошибка. Попробуйте еще раз",
	'YOUR_NICKNAME_NOW': "username={nickname}", # FORMAT: {nickname} - User Nickname
	'SNACKBAR_IN_MSGS_ON': "Уведомления в сообщениях включены",
	'SNACKBAR_IN_MSGS_OFF': "Уведомления в сообщениях выключены",
	'SNACKBAR_IN_MSGS_ASK': "Если вы не увидели снекбар, вы можете включить/отключить уведомления в сообщениях, используя !снекбар",
	'GREETING': ['дарова', 'ку', 'прив', 'здарова', 'категорически вас приветствую', 'здрассссссте']
}

import random

def txt(__name: str, *args, **kwargs):
	if __name not in msgs:
		return "NOT_FOUND: " + str(__name)
	v: str = msgs[__name]
	if type(v) == list:
		random.seed()
		v = v[round(random.random() * (v.__len__()-1))]
	try:
		v = v.format(*args, **kwargs)
	except: pass
	return v