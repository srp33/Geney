import json
from .Constants import *
from typing import Dict, Any

class MetaData:

	def __init__(self):
		self.__meta = {}
		self.__types = {}
		self.__ids = {}
		self.__features = None
		
	@property
	def meta_names(self):
		return sorted(self.__meta.keys())

	def get_meta_value(self, meta_name: str) -> Dict[str, Any]:
		return (self.__meta[meta_name] if meta_name in self.__meta else None)
		
	def get_meta_type(self, meta_name: str) -> str:
		return (self.__types[meta_name] if meta_name in self.__types else None)

	def get_meta_id(self, meta_name: str) -> int:
		return (self.__ids[meta_name] if meta_name in self.__ids else None)

	def add_meta(self, meta_type: str, meta_id: int, meta_name: str, meta_values: str) -> None:
		if meta_type == TEXT:
			self.__add_text_type(meta_name, meta_values)
		elif meta_type == REAL:
			self.__add_real_type(meta_name, meta_values)
		elif meta_type == INTEGER:
			self.__add_integer_type(meta_name, meta_values)
		else:
			raise Exception("Invalid meta type given")
		self.__types[meta_name] = meta_type
		self.__ids[meta_name] = meta_id

	def add_features(self, feature_count: int, features: Any) -> None:
		self.__features = {
			'numOptions': feature_count,
			'options': features,
		}

	def package(self) -> None:
		return {
			'meta': self.__meta,
			'features': self.__features,
		}

	def __add_text_type(self, meta_name: str, meta_values: str) -> None:
		value = {}
		meta_values = meta_values.split(',')
		value['numOptions'] = len(meta_values)
		if len(meta_values) < MAX_OPTIONS:
			value['options'] = list(meta_values)
		else:
			value['options'] = None
		self.__meta[meta_name] = value
		
	def __add_real_type(self, meta_name: str, meta_values: str) -> None:
		meta_values = [int(x) for x in meta_values.split(',')]
		assert(len(meta_values) == 2)
		self.__meta[meta_name] = {
			'options': 'continuous',
			'min': meta_values[0],
			'max': meta_values[1],
		}

	def __add_integer_type(self, meta_name: str, meta_values: str) -> None:
		meta_values = [float(x) for x in meta_values.split(',')]
		assert(len(meta_values) == 2)
		self.__meta[meta_name] = {
			'options': 'continuous',
			'min': meta_values[0],
			'max': meta_values[1],
		}
