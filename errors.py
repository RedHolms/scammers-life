# Errors handlers

import logging
log = logging.getLogger('scamLife.errors')

import sys
import traceback

def HandleError(cls, inst, trace):
	inst: cls
	if cls == SystemExit:
		log.info('Exiting with code ' + str(inst.code) + '...')
		raise SystemExit(inst.code)
	elif cls == ModuleNotFoundError:
		log.error('One of components doesn\'t installed')
		log.info('To install all components, run file: \'setup.py\'')
		log.info('Exiting with code 4...')
		raise SystemExit(4)
	else:
		log.error('Unhandled exception!')
		log.error('Error cls: ' + str(cls))
		_f_tb = traceback.format_exception(cls, value=inst, tb=trace)
		f_tb = ''
		for line in _f_tb:
			f_tb = f_tb + line
		log.error(f_tb)
		log.info('Exiting with code 2...')
		raise SystemExit(2)

def SetErrorHandler(f, *args, **kwargs):
	try: return f(*args, **kwargs)
	except:
		exc_info = sys.exc_info()
		cls, inst, trace = exc_info[0], exc_info[1], exc_info[2]
		try: 
			HandleError(cls, inst, trace)
		except:
			if sys.exc_info()[0] != SystemExit:
				print('[CRITICAL] ERROR WHILE HANDLING ERROR. Exit code: 100')
				raise sys.exc_info()[1]