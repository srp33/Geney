from datetime import datetime


class GeneyJob:
	def __init__(self, pid, path, email=None, name=None):
		self.pid = pid
		self.path = path
		self.email = email
		self.name = name
		self.date = datetime.utcnow()
