import json

KB_MENU = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'works',
						'payload': {}
					},
               "label":"💼 работы"
            },
            "color":"secondary"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'casino',
						'payload': {}
					},
               "label":"🎲 казик"
            },
            "color":"secondary"
			},
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'games',
						'payload': {}
					},
               "label":"🕹 игры"
            },
            "color":"secondary"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'shop',
						'payload': {}
					},
               "label":"🏪 магаз"
            },
            "color":"secondary"
			},
			{
            "action":{
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'vipshop',
						'payload': {}
					},
               "label":"🏛 банк"
            },
            "color":"secondary"
			},
			{
            "action":{
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'donate',
						'payload': {}
					},
               "label":"💸 донат"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'settings',
						'payload': {}
					},
               "label":"⚙ настроечьки"
            },
            "color":"secondary"
			},
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'promos',
						'payload': {}
					},
               "label":"🎟 промокоды"
            },
            "color":"positive"
			},
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'main_menu',
						'btype': 'reload',
						'payload': {}
					},
               "label":"поломалося("
            },
            "color":"secondary"
			}
		]
	]
})

KB_SETTINGS = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'settings',
						'btype': 'reload',
						'payload': {}
					},
               "label":"поломалося("
            },
            "color":"secondary"
			},
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'settings',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'settings',
						'btype': 'snackbar_switch',
						'payload': {}
					},
               "label":"Уведомления в сообщениях"
            },
            "color":"secondary"
			}
		]
	]
})

KB_SHOP = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'shop',
						'btype': 'dummy',
						'payload': {}
					},
               "label":"*"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'shop',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_VIPSHOP = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'vipshop',
						'btype': 'donate',
						'payload': {}
					},
               "label":"пополнить"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'vipshop',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_SHOP = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'shop',
						'btype': 'bank',
						'payload': {}
					},
               "label":"в банк!"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'shop',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_WORKSLIST = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workslist',
						'btype': 'work_scamavito',
						'payload': {}
					},
               "label":"скам на авито"
            },
            "color":"secondary"
			},
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workslist',
						'btype': 'work_fishing',
						'payload': {}
					},
               "label":"фишинг сайтов"
            },
            "color":"secondary"
			},
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workslist',
						'btype': 'thief',
						'payload': {}
					},
               "label":"воръ"
            },
            "color":"secondary"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workslist',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_CASINO = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'casino',
						'btype': 'onehandbandit',
						'payload': {}
					},
               "label":"однорукий бандит"
            },
            "color":"secondary"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'casino',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_GAMES = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'games',
						'btype': '2048',
						'payload': {}
					},
               "label":"2048"
            },
            "color":"secondary"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'games',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_GAMEMENU_2048 = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'gamemenu_2048',
						'btype': 'play',
						'payload': {}
					},
               "label":"играть"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'gamemenu_2048',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_DONATE = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'donate',
						'btype': 'dummy',
						'payload': {}
					},
               "label":"*"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'donate',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_WORKMENU_SCAM = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workmenu_scam',
						'btype': 'make_ad',
						'payload': {}
					},
               "label":"разместить объявление"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workmenu_scam',
						'btype': 'return',
						'payload': {
							'retTo': 'WorksList'
						}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_WORKMENU_SCAM_R = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workmenu_scam',
						'btype': 'return',
						'payload': {
							'retTo': 'WorksList'
						}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_WORKMENU_THIEF = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'workmenu_thief',
						'btype': 'return',
						'payload': {
							'retTo': 'WorksList'
						}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_PROMOS = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'promos',
						'btype': 'create',
						'payload': {}
					},
               "label":"создать промокод"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'promos',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KB_PROMOS_H = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'promos',
						'btype': 'manage',
						'payload': {}
					},
               "label":"управление промокодом"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'promos',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KBU_RETURN = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'UNIVERSAL',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KBU_PLACEHOLDER = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'UNIVERSAL',
						'btype': 'dummy',
						'payload': {}
					},
               "label":"*"
            },
            "color":"primary"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'UNIVERSAL',
						'btype': 'return',
						'payload': {}
					},
               "label":"назад"
            },
            "color":"secondary"
			}
		]
	]
})

KBU_CONFIRM = json.dumps({
	"one_time": False,
	"inline": False,
	"buttons": [
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'UNIVERSAL',
						'btype': 'confirm',
						'payload': {}
					},
               "label":"подтвердить"
            },
            "color":"positive"
			}
		],
		[
			{
            "action":{  
               "type":"callback",
               "payload": {
						'ktype': 'UNIVERSAL',
						'btype': 'decline',
						'payload': {}
					},
               "label":"отменить"
            },
            "color":"negative"
			}
		]
	]
})

def keyboard(kb: str, **kwargs):
	_kb = json.loads(kb)
	lineI = 0
	for line in _kb['buttons']:
		btnI = 0
		for btn in line:
			for name, arg in kwargs.items():
				if btn['action']['payload']['btype'] == name:
					if type(arg) == bool:
						_kb['buttons'][lineI][btnI]['color'] = 'positive' if arg else 'negative'
					elif type(arg) == str:
						_kb['buttons'][lineI][btnI]['label'] = arg
					elif type(arg) == dict:
						_kb['buttons'][lineI][btnI]['action']['payload']['payload'] = arg
			btnI += 1
		lineI += 1
	return json.dumps(_kb)