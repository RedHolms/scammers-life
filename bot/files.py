import logging
log = logging.getLogger('scamLife.bot.files')

from . import vk_api
from . import post_manager as pm

import requests
import json

class FileLoader(object):
	def __init__(self, api: vk_api.ApiSession, group_id: int, bot_album: int) -> None:
		self.api = api
		self.group_id = group_id

		self.bot_album = bot_album
		
		self.imagesInfo = {}
		self.post = pm.Multipart_FormData()

	def _format_bytearray_to_http(self, b: bytearray) -> str:
		c = ''
		for byte in b:
			c += chr(byte)
		return c
	
	def LoadImage(self, fPath: str) -> str:
		if fPath in self.imagesInfo:
			return self.imagesInfo[fPath]
		
		fPath = 'bot\\rsc\\' + fPath

		with open(fPath, 'rb') as f:
			content = bytearray(f.read())
			f.close()
		
		r = self.api.executeMethod('photos.getMessagesUploadServer', {
			'group_id': self.group_id
		})

		fname = fPath.split('\\')
		fname = fname[fname.__len__() - 1]
		fext = fname.split('.')
		fext = fext[fext.__len__() - 1]

		ctype = 'image/' + ('jpeg' if fext == 'jpg' else fext)

		r = self.post.SendPost(r['upload_url'], [pm.FormData_File('photo', fname, ctype, self._format_bytearray_to_http(content))])
		r = r.json()
		log.debug('Image "' + fPath + '" loaded, response=' + str(r) + '\n')

		r = self.api.executeMethod('photos.saveMessagesPhoto', {
			'server': r['server'],
			'photo': r['photo'],
			'hash': r['hash']
		})[0]
		log.debug('Image "' + fPath + '" saved, response=' + str(r))
		img_id = str(r['owner_id']) + '_' + str(r['id'])
		self.imagesInfo[fPath] = img_id
		return img_id

		