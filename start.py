import logging
import sys

from bot.sql import SQL

TOKEN = ''
GROUP_ID = 0
ADMIN = 0

"""
int			 nvarchar(32)	 smallint	 bigint			 bit				 bit						 nvarchar(90)	 nvarchar(90) 	; type

UNIQUE																																						; constraints
NOT NULL

vkId			| nickname		| state		| lastEvent		| registred		| infoInitialized		| userName		| userSurname	; columns
"""

def main():
	import bot

	log = logging.getLogger('scamLife.start[main]')
	
	log.debug('Reading auth info...')
	try:
		with open('AUTH_INFO', 'r') as f:
			TOKEN = f.readline()
			GROUP_ID = f.readline()
			ADMIN = f.readline()
			if TOKEN.endswith('\n'): TOKEN = TOKEN[:TOKEN.__len__() - 1]
			if GROUP_ID.endswith('\n'): GROUP_ID = GROUP_ID[:GROUP_ID.__len__() - 1]
			if ADMIN.endswith('\n'): ADMIN = ADMIN[:ADMIN.__len__() - 1]
			GROUP_ID = int(GROUP_ID)
			ADMIN = int(ADMIN)
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
		SQLfield('nickname', 'nvarchar(32)'),
		SQLfield('state', 'smallint'),
		SQLfield('lastEvent', 'bigint'),
		SQLfield('registred', 'bit'),
		SQLfield('infoInitialized', 'bit'),
		SQLfield('userName', 'nvarchar(90)'),
		SQLfield('userSurname', 'nvarchar(90)'),
		SQLfield('money', 'money'),
		SQLfield('admin', 'bit'),
		SQLfield('snackbarsInMsg', 'bit'),
		SQLfield('flags', 'bigint')
	])
	db.UpdateRow(ADMIN, 'admin', 1)

	log.debug('Starting bot...')
	_bot = bot.Bot(bot.vk_api.ApiSession(TOKEN), GROUP_ID, db)
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