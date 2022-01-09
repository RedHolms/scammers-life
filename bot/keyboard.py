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
						'ktype': 'main_menu',
						'btype': 'dummy',
						'payload': {}
					},
               "label":"DUMMY"
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
						'btype': 'dummy',
						'payload': {}
					},
               "label":"DUMMY"
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
						'btype': 'dummy',
						'payload': {}
					},
               "label":"DUMMY"
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
						'btype': 'settings',
						'payload': {}
					},
               "label":"⚙ настроечьки"
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
			btnI += 1
		lineI += 1
	return json.dumps(_kb)