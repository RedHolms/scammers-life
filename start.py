import logging
import sys
import json

TOKEN = ''
GROUP_ID = 0
ADMIN = 0
IMG_ALBUM = 0

def main():
	import bot

	log = logging.getLogger('scamLife.start[main]')
	
	log.debug('Reading auth info...')
	try:
		with open('AUTH_INFO.json', 'r', encoding='utf-8') as f:
			auth = json.load(f)
			TOKEN = auth['token']
			GROUP_ID = auth['group_id']
			ADMIN = auth['admin']
			IMG_ALBUM = auth['img_album']
			f.close()
	except FileNotFoundError:
		log.error('Auth info not found')
		log.info('To start bot an Auth info needed')
		log.info('Contact with distributer for more information')
		raise SystemExit(3)
	
	log.debug('Loading DB...')
	SQLfield = bot.sql.SQLfield
	db = bot.sql.SQL('SCAM_LIFE.sqlite', [
		SQLfield('id', 'bigint', ['UNIQUE', 'NOT NULL']),
		SQLfield('nickname', 'nvarchar(20)'),
		SQLfield('state', 'smallint'),
		SQLfield('lastEvent', 'bigint'),
		SQLfield('registred', 'bit'),
		SQLfield('infoInitialized', 'bit'),
		SQLfield('userName', 'nvarchar(90)'),
		SQLfield('userSurname', 'nvarchar(90)'),
		SQLfield('money', 'money'),
		SQLfield('admin', 'bit'),
		SQLfield('snackbarsInMsg', 'bit'),
		SQLfield('flags', 'bigint'),
		SQLfield('euro', 'money'),
		SQLfield('scam_adName', 'nvarchar(32)'),
		SQLfield('scam_adDesc', 'nvarchar(92)'),
		SQLfield('scam_adCreate', 'bigint'),
		SQLfield('scam_adEnd', 'int'),
		SQLfield('maxScore2048', 'int')
	])
	db.UpdateRow(ADMIN, 'admin', 1)

	log.debug('Starting bot...')
	_bot = bot.Bot(bot.vk_api.ApiSession(TOKEN), GROUP_ID, db, IMG_ALBUM)
	_bot.Start()

if __name__ == '__main__':
	from errors import SetErrorHandler

	DebugEnabled = '--debug' in sys.argv

	log = logging.getLogger('scamLife')
	formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] (%(levelname)s) %(name)s: %(message)s', '%H:%M:%S')
	log.setLevel(logging.DEBUG if DebugEnabled else logging.INFO)

	fh = logging.FileHandler("scammers-life.log", 'w')
	fh.setFormatter(formatter)
	log.addHandler(fh)

	sh = logging.StreamHandler(sys.stdout)
	sh.setFormatter(formatter)
	log.addHandler(sh)

	log.info('Logger intitialized')

	log = logging.getLogger('scamLife.start')

	log.debug('Initializing error handling...')
	
	SetErrorHandler(main)