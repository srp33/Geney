# import json
# import hashlib
# from typing import Dict, List, Any
#
#
# class Filter:
# 	def __init__(self, name, values):
# 		self.__name = name
# 		self.__values = values
#
# 	@property
# 	def name(self):
# 		return self.__name
#
# 	@property
# 	def values(self):
# 		return self.__values
#
# 	@property
# 	def md5(self) -> str:
# 		return hashlib.md5(
# 			json.dumps(
# 				{ self.__name: self.__values }
# 			).encode('utf-8')
# 		).hexdigest()
#
#
# class FilterIter:
# 	def __init__(self, filter_def: Dict[str, List[Any]]):
# 		self.__def = filter_def
# 		self.__names = iter(filter_def.keys())
#
# 	def __iter__(self):
# 		return self
#
# 	def __next__(self):
# 		self.__current_name = next(self.__names)
# 		return Filter(self.__current_name, self.__def[self.__current_name])
