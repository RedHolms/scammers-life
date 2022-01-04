if __name__ == '__main__':
	import logging
	import time
	import sys
	import traceback

	DebugEnabled = '--debug' in sys.argv

	log = logging.getLogger('scamLife')
	formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] (%(levelname)s) - %(name)s: %(message)s', '%H:%M:%S')
	log.setLevel(logging.DEBUG if DebugEnabled else logging.INFO)

	fh = logging.FileHandler("scammers-life.log", 'w')
	fh.setFormatter(formatter)
	log.addHandler(fh)

	sh = logging.StreamHandler(sys.stdout)
	sh.setFormatter(formatter)
	log.addHandler(sh)

	log.info('Logger intitialized')

	log = logging.getLogger('scamLife.start')

	log.debug('Settings up main except block...')
	try:
		log.info('Stated at: ' + str(time.time()))

		import bot

		log.debug('Loading auth info...')

		TOKEN, GROUP_ID = None, None
		try:
			with open('AUTH_INFO', 'r') as f:
				TOKEN = f.readline()
				GROUP_ID = f.readline()

				if TOKEN.endswith('\n'): TOKEN = TOKEN[:TOKEN.__len__() - 1]
				if GROUP_ID.endswith('\n'): GROUP_ID = GROUP_ID[:GROUP_ID.__len__() - 1]

				try:
					GROUP_ID = int(GROUP_ID)
				except ValueError:
					log.critical('Can\'t parse group id to number')
					raise SystemExit(1)
		except FileNotFoundError as e:
			log.critical('Auth Info not found')
			raise SystemExit(1)
		
		log.debug('Auth info loaded')
		if DebugEnabled:
			ans = input('Do you want to print token?[Y to agree] ')
			if ans.lower() == 'y':
				log.debug('Token=' + str(TOKEN))
		log.debug('Group id=' + str(GROUP_ID))

		log.debug('Creating VK api session...')
		apiSession = bot.vk_api.ApiSession(TOKEN)

		log.debug('Creating bot instance...')
		Bot = bot.Bot(apiSession, GROUP_ID)

		log.debug('Starting...')
		Bot.start()
	except:
		exc_info = sys.exc_info()
		exc, inst, trace = exc_info[0], exc_info[1], exc_info[2]

		if exc == SystemExit:
			log.info('Exiting with code <' + str(inst.code) + '>...')
			raise inst
		else:
			log.error('Uncaught error! Error class: ' + str(exc))
			log.error(traceback.format_exc())
			log.error('_________')
			log.error('Error info: ' + str(inst))
			log.info('Exiting with code <2>...')
			raise SystemExit(2)