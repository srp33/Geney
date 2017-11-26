import json, hashlib
from typing import List, Tuple, Any, Iterator
from jsonschema import validate, ValidationError
from .Filter import MetaFilter, MetaFilterIter
from .Exceptions import RequestError

with open('schemas/query.json', 'r') as schema_file:
	QUERY_SCHEMA = json.load(schema_file)

class Query:
	def __init__(self, query_def, dataset_description):
		try:
			validate(query_def, QUERY_SCHEMA)
			self.valid = True
			self.__def = query_def
			self.__max_features = dataset_description['numFeatures']
		except ValidationError:
			raise RequestError('Could not validate query definition')

	@property
	def meta_filters(self) -> Iterator[MetaFilter]:
		return MetaFilterIter(self.__def['filters'])

	@property
	def meta_filter_names(self) -> List[str]:
		return self.__def['metaTypes']

	@property
	def feature_filters(self) -> List[str]:
		return self.__def['features'] if len(self.__def['features']) > 0 else None

	@property
	def num_features(self) -> bool:
		num_feature_filters = len(self.__def['features'])
		return num_feature_filters if num_feature_filters > 0 else self.__max_features

	@property
	def md5(self) -> str:
		return hashlib.md5(json.dumps(self.__def).encode('utf-8')).hexdigest()
