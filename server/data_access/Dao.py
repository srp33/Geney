import sqlite3, h5py
from typing import List, Set, Dict, Any, Tuple
import numpy as np
from .Constants import *
from .Query import Query, MetaFilter
from .Exceptions import RequestError, ServerError

class SQLiteDao:

	def __init__(self, directory):
		self.__con = sqlite3.connect('file:{file_path}?mode=ro'.format(file_path=(directory + METADATA_DB)), uri=True)

	def __enter__(self):		
		return self

	def __exit__(self, type, value, traceback):
		self.close()

	def close(self):
		self.__con.close()
	
	def get_variable(self, variable_name) -> Tuple[str,str]:
		cursor = self.__con.cursor()
		variable = cursor.execute(GET_VARIABLE, (variable_name,)).fetchone()
		cursor.close()
		return variable		

	def get_samples_matching_filter(self, meta_filter: MetaFilter) -> Set[int]:
		# get table to search for dataset ids
		meta_id, meta_type = self.get_variable(meta_filter.name)
		values = meta_filter.values
		if meta_type == TEXT:
			return self.__filter_text(meta_id, values)
		elif meta_type == INTEGER:
			return self.__filter_integer(meta_id, values)
		elif meta_type == REAL:
			return self.__filter_real(meta_id, values)
		else:
			return None

	def __filter_text(self, meta_id: int, values: List[str]) -> Set[int]:
		try:
			# build query
			query = GET_SAMPLEID_TEXT_TABLE.format(var_id=meta_id, items='"{}"'.format('","'.join(values)))
			assert(self.__valid_meta_filter_query(query, discrete=True))
			# now we know it's a valid query, so execute it and get ids
			ids = set()
			cursor = self.__con.cursor()
			for sample_id in cursor.execute(query):
				ids.add(sample_id[0])
			# cleanup and return
			cursor.close()			
			return ids

		except ValueError as ve:
			# the .format received the wrong parameter types
			raise RequestError('Could not build discrete query with meta_id "{}"'.format(meta_id))
		except AssertionError as ae:
			# the regex failed to match
			raise RequestError('Invalid discrete query: {}'.format(query))

	def __filter_integer(self, meta_id: int, values: List[str]) -> Set[int]:
		raise NotImplementedError()

	def __filter_real(self, meta_id: int, values: List[str]) -> Set[int]:
		raise NotImplementedError()

	def __valid_meta_filter_query(self, query: str, discrete=False, continuous=False) -> bool:
		return (discrete and DISCRETE_QUERY_REGEX.match(query) is not None) or (continuous and CONTINUOUS_QUERY_REGEX.match(query)) 

	def get_feature_ids(self, feature_filters: List[str]) -> List[int]:
		query = GET_FEATURE_IDS.format(items='"{}"'.format('","'.join(feature_filters)))
		# TODO validate query against SQL injection
		requested_features = set(feature_filters)
		feature_ids = list()
		cursor = self.__con.cursor()
		for feature in cursor.execute(query):
			feature_ids.append(feature[0])
			requested_features.remove(feature[1])
		
		cursor.close()
		
		if len(requested_features) > 0:
			raise RequestError('Unknown features: {}'.format(', '.join(requested_features)))

		return feature_ids

	def get_sample_metadata(self, sample_id: int, meta_names: List[str]) -> Dict[str, Any]:
		# for details on ** see https://www.python.org/dev/peps/pep-0448/
		meta_names_str = '"{}"'.format('","'.join(meta_names))
		# TODO validate the queries made in the below functions with a 
		return {
			**self.__get_sample_metadata('textTable', sample_id, meta_names_str), 
			**self.__get_sample_metadata('integerTable', sample_id, meta_names_str), 
			**self.__get_sample_metadata('realTable', sample_id, meta_names_str), 
		}

	def get_sample_name(self, sample_id: int) -> str:
		cursor = self.__con.cursor()
		name = cursor.execute(GET_SAMPLE_NAME, (sample_id,)).fetchone()[0]
		cursor.close()
		return name

	def __get_sample_metadata(self, table: str, sample_id: int, meta_names: str) -> Dict[str, str]:
		metadata = {}
		cursor = self.__con.cursor()
		query = GET_SAMPLE_METADATA_FROM_TABLE_X.format(x=table, sample_id=sample_id, items=meta_names)
		for meta in cursor.execute(query):
			metadata[meta[0]] = meta[1]
		cursor.close()
		return metadata

	def get_all_feature_names(self) -> List[str]:
		names = list()
		cursor = self.__con.cursor()
		for feature in cursor.execute(GET_ALL_FEATURE_NAMES):
			names.append(feature[0])
		cursor.close()	
		return names	

	def search_features(self, search_val:str) -> List[str]:
		names = list()
		cursor = self.__con.cursor()
		for feature in cursor.execute(SEARCH_FEATURES, ('%{}%'.format(search_val),)):
			names.append(feature[0])
		cursor.close()	
		return names			

	def search_meta_type(self, meta_type: str, search_val: str) -> List[str]:
		values = list()
		meta_id, meta_type = self.get_variable(meta_type)
		if meta_type != TEXT:
			return None
		cursor = self.__con.cursor()
		for variable in cursor.execute(SEARCH_TEXT_META_TYPE, (meta_id,'%{}%'.format(search_val))):
			values.append(variable[0])
		cursor.close()	
		return values			

	def search_meta_types(self, search_val:str) -> List[str]:
		names = list()
		cursor = self.__con.cursor()
		for feature in cursor.execute(SEARCH_VARIABLES, ('%{}%'.format(search_val),)):
			names.append(feature[0])
		cursor.close()	
		return names			

	def get_variable_options(self, variable_name):
		variable = self.get_variable(variable_name)		
		if variable is None:
			return None
		meta_id, meta_type = variable
		cursor = self.__con.cursor()
		row = cursor.execute(GET_VARIABLE_OPTIONS, (meta_id,)).fetchone()
		if row is None:
			return None
		numOptions, options = row
		cursor.close()
		if meta_type == TEXT:
			if options == 'null':
				options = None
			else:
				options = options.split(',')			
			return { "numOptions": numOptions, "options": options }
		else:
			if meta_type == INTEGER:
				min_val, max_val = [int(x) for x in options.split(',')]
			elif meta_type == REAL:
				min_val, max_val = [float(x) for x in options.split(',')]
			else: # if it's not D
				return None
			return { "min": min_val, "max": max_val, "options": "continuous" }

class Hdf5Dao:

	def __init__(self, directory):
		self.__hdf5 = h5py.File(directory + DATA_FILE, 'r')
		self.__data = self.__hdf5[HDF5_DATA_PATH]
		# print(self.__data[0][0].astype(str))
		# print(str(self.__data[0][0]))

	def get_row(self, row_index, col_indices, num_features) -> List[str]:
		for start, end in col_indices:
			yield self.__data[row_index, start:end].astype(str)

	def close(self):
		self.__hdf5.close()
