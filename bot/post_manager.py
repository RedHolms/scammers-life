import requests
import time

class FormData_File(object):
	def __init__(self, name: str, filename: str, content_type: str, content: str) -> None:
		self.name = name
		self.filename = filename
		self.content_type = content_type
		self.content = content

class Multipart_FormData(object):
	def __init__(self, boundary: str = None) -> None:
		self.session = requests.Session()

		if boundary == None:
			boundary = '--' + str(round(time.time())) + '--'
		if type(boundary) != str: boundary = str(boundary)

		self.session.headers['Content-Type'] = 'multipart/form-data; boundary=' + boundary
		self.boundary = boundary
	def SendPost(self, url: str, files: list[FormData_File]) -> requests.Response:
		nl = '\r\n'
		for f in files:
			content = '--' + self.boundary + nl
			content += f'Content-Disposition: form-data; name={f.name}; filename="{f.filename}"' + nl
			content += f'Content-Type: ' + f.content_type + nl + nl
			content += f.content + nl
		content += '--' + self.boundary + '--'
		return self.session.request('POST', url, data=content, headers={
			'Content-Length': str(len(content))
		})
