import json, hashlib
from typing import Dict, List, Any

class MetaFilter:
	def __init__(self, name, values):
		self.__name = name
		self.__values = values

	@property
	def name(self):
		return self.__name

	@property
	def values(self):
		return self.__values

	@property
	def md5(self) -> str:
		return hashlib.md5(
			json.dumps(
				{ self.__name: self.__values }
			).encode('utf-8')
		).hexdigest()

class MetaFilterIter:
	def __init__(self, meta_def: Dict[str, List[Any]]):
		self.__meta_def = meta_def
		self.__names = iter(meta_def.keys())

	def __iter__(self):
		return self
 
	def __next__(self):
		self.__current_name = next(self.__names)
		return MetaFilter(self.__current_name, self.__meta_def[self.__current_name])
