import logging
import sys

import bot

TOKEN = ''
GROUP_ID = 0

def main():
	log = logging.getLogger('scamLife.start[main]')
	
	log.debug('Reading auth info...')
	try:
		with open('AUTH_INFO', 'r') as f:
			TOKEN = f.readline()
			GROUP_ID = f.readline()
			if TOKEN.endswith('\n'): TOKEN = TOKEN[:TOKEN.__len__() - 1]
			if GROUP_ID.endswith('\n'): GROUP_ID = GROUP_ID[:GROUP_ID.__len__() - 1]
			GROUP_ID = int(GROUP_ID)
			f.close()
	except FileNotFoundError:
		log.error('Auth info not found')
		log.info('To start bot Auth info needed')
		log.info('Contact with distributer for more information')
		raise SystemExit(3)

	log.debug('Starting bot...')
	_bot = bot.Bot(bot.vk_api.ApiSession(TOKEN), GROUP_ID)
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