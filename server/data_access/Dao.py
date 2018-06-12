import h5py
import sqlite3
import time
from typing import List, Set, Dict, Any, Tuple

import UseParquet as ss
from .Constants import *
# from .Exceptions import RequestError
from .Query import Query
import os
import uuid

# class SQLiteDao:
#
# 	def __init__(self, directory):
# 		self.__con = sqlite3.connect('file:{file_path}?mode=ro'.format(file_path=(directory + METADATA_DB)), uri=True)
#
# 	def __enter__(self):
# 		return self
#
# 	def __exit__(self, type, value, traceback):
# 		self.close()
#
# 	def close(self):
# 		self.__con.close()
#
# 	def get_variable(self, variable_name) -> Tuple[str,str]:
# 		cursor = self.__con.cursor()
# 		variable = cursor.execute(GET_VARIABLE, (variable_name,)).fetchone()
# 		cursor.close()
# 		return variable
#
# 	def get_samples_matching_filter(self, meta_filter: MetaFilter) -> Set[int]:
# 		# get table to search for dataset ids
# 		meta_id, meta_type = self.get_variable(meta_filter.name)
# 		values = meta_filter.values
# 		if meta_type.lower() == TEXT:
# 			return self.__filter_text(meta_id, values)
# 		elif meta_type.lower() == INTEGER:
# 			return self.__filter_integer(meta_id, values)
# 		elif meta_type.lower() == REAL:
# 			return self.__filter_real(meta_id, values)
# 		else:
# 			return None
#
# 	def __filter_text(self, meta_id: int, values: List[str]) -> Set[int]:
# 		if len(values) == 0 or type(values[0]) is not str:
# 			return set()
#
# 		try:
# 			# build query
# 			query = GET_SAMPLEID_TEXT_TABLE.format(var_id=meta_id, items='"{}"'.format('","'.join(values)))
# 			assert(self.__valid_meta_filter_query(query, discrete=True))
# 			# now we know it's a valid query, so execute it and get ids
# 			ids = set()
# 			cursor = self.__con.cursor()
# 			for sample_id in cursor.execute(query):
# 				ids.add(sample_id[0])
# 			# cleanup and return
# 			cursor.close()
# 			return ids
#
# 		except ValueError as ve:
# 			# the .format received the wrong parameter types
# 			raise RequestError('Could not build text query with meta_id "{}"'.format(meta_id))
# 		except AssertionError as ae:
# 			# the regex failed to match
# 			raise RequestError('Invalid text query: {}'.format(query))
#
# 	def __filter_integer(self, meta_id: int, values: List[str]) -> Set[int]:
# 		if len(values) == 0 or type(values[0]) is not dict:
# 			return set()
#
# 		try:
# 			print(meta_id, values)
# 			whereStatements = ['value {operator} {value}'.format(operator=x['operator'], value=x['value']) for x in values ]
# 			query = GET_SAMPLEID_INTEGER_TABLE.format(var_id=meta_id, where=' AND '.join(whereStatements))
# 			assert(self.__valid_meta_filter_query(query, continuous=True))
# 			# now we know it's a valid query, so execute it and get ids
# 			ids = set()
# 			cursor = self.__con.cursor()
# 			for sample_id in cursor.execute(query):
# 				ids.add(sample_id[0])
# 			# cleanup and return
# 			cursor.close()
# 			return ids
#
# 		except ValueError as ve:
# 			# the .format received the wrong parameter types
# 			raise RequestError('Could not build integer query with meta_id "{}"'.format(meta_id))
# 		except AssertionError as ae:
# 			# the regex failed to match
# 			raise RequestError('Invalid text query: {}'.format(query))
#
# 	def __filter_real(self, meta_id: int, values: List[str]) -> Set[int]:
# 		if len(values) == 0 or type(values[0]) is not dict:
# 			return set()
#
# 		try:
# 			print(meta_id, values)
# 			whereStatements = ['value {operator} {value}'.format(operator=x['operator'], value=x['value']) for x in values]
# 			query = GET_SAMPLEID_REAL_TABLE.format(var_id=meta_id, where=' AND '.join(whereStatements))
# 			assert(self.__valid_meta_filter_query(query, continuous=True))
# 			# now we know it's a valid query, so execute it and get ids
# 			ids = set()
# 			cursor = self.__con.cursor()
# 			for sample_id in cursor.execute(query):
# 				ids.add(sample_id[0])
# 			# cleanup and return
# 			cursor.close()
# 			return ids
#
# 		except ValueError as ve:
# 			# the .format received the wrong parameter types
# 			raise RequestError('Could not build integer query with meta_id "{}"'.format(meta_id))
# 		except AssertionError as ae:
# 			# the regex failed to match
# 			raise RequestError('Invalid text query: {}'.format(query))
#
# 	def __valid_meta_filter_query(self, query: str, discrete=False, continuous=False) -> bool:
# 		return (discrete and DISCRETE_QUERY_REGEX.match(query) is not None) or (continuous and CONTINUOUS_QUERY_REGEX.match(query))
#
# 	def get_feature_ids(self, feature_filters: List[str]) -> List[int]:
# 		query = GET_FEATURE_IDS.format(items='"{}"'.format('","'.join(feature_filters)))
# 		# TODO validate query against SQL injection
# 		requested_features = set(feature_filters)
# 		feature_ids = list()
# 		cursor = self.__con.cursor()
# 		for feature in cursor.execute(query):
# 			feature_ids.append(feature[0])
# 			requested_features.remove(feature[1])
#
# 		cursor.close()
#
# 		if len(requested_features) > 0:
# 			raise RequestError('Unknown features: {}'.format(', '.join(requested_features)))
#
# 		return feature_ids
#
# 	def get_sample_ids(self, sample_names: List[str]) -> List[int]:
# 		query = GET_SAMPLE_IDS.format(items='"{}"'.format('","'.join(sample_names)))
# 		sampleIDs = []
# 		cursor = self.__con.cursor()
# 		for sampleID in cursor.execute(query):
# 			sampleIDs.append(int(sampleID[0]))
# 		cursor.close()
# 		return sampleIDs
#
# 	def get_all_sample_ids(self) -> List[int]:
# 		sampleIDs = []
# 		cursor = self.__con.cursor()
# 		for sampleID in cursor.execute(GET_ALL_SAMPLE_IDS):
# 			sampleIDs.append(int(sampleID[0]))
# 		cursor.close()
# 		return sampleIDs
#
# 	def get_sample_metadata(self, sample_id: int, meta_names: List[str]) -> Dict[str, Any]:
# 		# for details on ** see https://www.python.org/dev/peps/pep-0448/
# 		meta_names_str = '"{}"'.format('","'.join(meta_names))
# 		# TODO validate the queries made in the below functions with a
# 		return {
# 			**self.__get_sample_metadata('textTable', sample_id, meta_names_str),
# 			**self.__get_sample_metadata('integerTable', sample_id, meta_names_str),
# 			**self.__get_sample_metadata('realTable', sample_id, meta_names_str),
# 		}
#
# 	def get_sample_name(self, sample_id: int) -> str:
# 		cursor = self.__con.cursor()
# 		result = cursor.execute(GET_SAMPLE_NAME, (sample_id,)).fetchone()
# 		name = result[0] if result is not None else ''
# 		cursor.close()
# 		return name
#
# 	def __get_sample_metadata(self, table: str, sample_id: int, meta_names: str) -> Dict[str, str]:
# 		metadata = {}
# 		cursor = self.__con.cursor()
# 		query = GET_SAMPLE_METADATA_FROM_TABLE_X.format(x=table, sample_id=sample_id, items=meta_names)
# 		for meta in cursor.execute(query):
# 			meta_name = meta[0]
# 			val = meta[1] if table == 'textTable' else str(meta[1])
# 			if meta[0] in metadata:
# 				if not table == 'textTable':
# 					raise Exception('multiple values for non discrete meta type')
# 				metadata[meta_name] += '|' + val
# 			else:
# 				metadata[meta_name] = val
# 		cursor.close()
# 		return metadata
#
# 	def get_all_feature_names(self) -> List[str]:
# 		names = list()
# 		cursor = self.__con.cursor()
# 		for feature in cursor.execute(GET_ALL_FEATURE_NAMES):
# 			names.append(feature[0])
# 		cursor.close()
# 		return names
#
# 	def get_all_variable_names(self) -> List[str]:
# 		names = list()
# 		cursor = self.__con.cursor()
# 		for feature in cursor.execute(GET_ALL_VARIABLE_NAMES):
# 			names.append(feature[0])
# 		cursor.close()
# 		return names
#
# 	def search_features(self, search_val:str) -> List[str]:
# 		names = list()
# 		cursor = self.__con.cursor()
# 		for feature in cursor.execute(SEARCH_FEATURES, ('%{}%'.format(search_val),)):
# 			names.append(feature[0])
# 		cursor.close()
# 		return names
#
# 	def search_sample_id(self, search_val: str) -> List[str]:
# 		names = list()
# 		cursor = self.__con.cursor()
# 		for feature in cursor.execute(SEARCH_SAMPLES, ('%{}%'.format(search_val),)):
# 			names.append(feature[0])
# 		cursor.close()
# 		return names
#
# 	def search_meta_type(self, meta_type: str, search_val: str) -> List[str]:
# 		values = list()
# 		result = self.get_variable(meta_type)
# 		if result is None:
# 			return None
# 		meta_id, meta_type = result
# 		if meta_type != TEXT:
# 			return None
# 		cursor = self.__con.cursor()
# 		for variable in cursor.execute(SEARCH_TEXT_META_TYPE, (meta_id,'%{}%'.format(search_val))):
# 			values.append(variable[0])
# 		cursor.close()
# 		return values
#
# 	def search_meta_types(self, search_val:str) -> List[str]:
# 		names = list()
# 		cursor = self.__con.cursor()
# 		for feature in cursor.execute(SEARCH_VARIABLES, ('%{}%'.format(search_val),)):
# 			names.append(feature[0])
# 		cursor.close()
# 		return names
#
# 	def get_variable_options(self, variable_name) -> Dict[str, Any]:
# 		variable = self.get_variable(variable_name)
# 		if variable is None:
# 			return None
# 		meta_id, meta_type = variable
# 		cursor = self.__con.cursor()
# 		row = cursor.execute(GET_VARIABLE_OPTIONS, (meta_id,)).fetchone()
# 		if row is None:
# 			return None
# 		numOptions, options = row
# 		cursor.close()
# 		if meta_type == TEXT:
# 			if options == 'null':
# 				options = None
# 			else:
# 				options = options.split(',')
# 			return { "numOptions": numOptions, "options": options }
# 		else:
# 			if meta_type == INTEGER:
# 				min_val, max_val = [int(x) for x in options.split(',')]
# 			elif meta_type == REAL:
# 				min_val, max_val = [float(x) for x in options.split(',')]
# 			else: # if it's not D
# 				return None
# 			return { "min": min_val, "max": max_val, "options": "continuous" }
#
# 	def get_sample_id_options(self) -> Dict[str, Any]:
# 		cursor = self.__con.cursor()
# 		options = []
# 		for sample in cursor.execute(GET_ALL_SAMPLE_NAMES):
# 			options.append(sample[0])
# 		cursor.close()
# 		return options

class Hdf5Dao:

	def __init__(self, directory):
		self.__hdf5 = h5py.File(directory + DATA_FILE, 'r')
		self.__data = self.__hdf5[HDF5_DATA_PATH]

	def get_row(self, row_index, col_indices) -> List[str]:
		for start, end in col_indices:
			yield self.__data[row_index, start:end].astype(str)

	def close(self):
		self.__hdf5.close()

class ParquetDao:

	def __init__(self, directory):
		# self.__file = directory
		self.__file = "{}{}".format(directory, DATA_FILE)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		return exc_val

	def get_variables(self):
		return ss.getColumnNames(self.__file)

	def get_samples_from_query(self, query: Query):
		continuous_filters = []
		discrete_filters = []
		for filter in query.filters:
			values = filter.values
			if type(values[0]) != str:
				for value in values:
					operatorEnum = None
					if value['operator'] is '>':
						operatorEnum = ss.OperatorEnum.GreaterThan
					elif value['operator'] is '<':
						operatorEnum = ss.OperatorEnum.LessThan
					elif value['operator'] is '<=':
						operatorEnum = ss.OperatorEnum.LessThanOrEqualTo
					elif value['operator'] is '>=':
						operatorEnum = ss.OperatorEnum.GreaterThanOrEqualTo
					elif value['operator'] is '!=':
						operatorEnum = ss.OperatorEnum.NotEquals
					elif value['operator'] is '==':
						operatorEnum = ss.OperatorEnum.Equals
					if operatorEnum:
						continuous_filters.append(ss.ContinuousQuery(filter.name, operatorEnum, value['value']))
			else:
				discrete_filters.append(ss.DiscreteQuery(filter.name, values))
		df = ss.query(self.__file, discreteQueries=discrete_filters, continuousQueries=continuous_filters)
		return df.index.values

	def get_file_from_query(self, query: Query, features, file_format, dataset_id, download_location):
		filename = dataset_id + uuid.uuid4().hex[:8]
		if file_format is 'csv':
			file_type = ss.FileTypeEnum.CSV
			filename += ".csv"
		elif file_format is 'json':
			file_type = ss.FileTypeEnum.JSON
			filename += ".json"
		elif file_format is 'pickle':
			file_type = ss.FileTypeEnum.Pickle
			filename += '.pkl'
		elif file_format is 'tsv':
			file_type = ss.FileTypeEnum.TSV
			filename += '.tsv'
		elif file_format is 'hdf5':
			file_type = ss.FileTypeEnum.HDF5
			filename += '.h5'
		elif file_format is 'arff':
			file_type = ss.FileTypeEnum.ARFF
			filename += '.arff'
		elif file_format is 'excel':
			file_type = ss.FileTypeEnum.Excel
			filename += '.xlsx'
		elif file_format is 'feather':
			file_type = ss.FileTypeEnum.Feather
			filename += '.feather'
		elif file_format is 'msgpack':
			file_type = ss.FileTypeEnum.MsgPack
			filename += '.msgpack'
		elif file_format is 'parquet':
			file_type = ss.FileTypeEnum.Parquet
			filename += '.pq'
		elif file_format is 'stata':
			file_type = ss.FileTypeEnum.Stata
			filename += '.dta'
		elif file_format is 'sqlite':
			file_type = ss.FileTypeEnum.SQLite
			filename += '.sql'
		elif file_format is 'html':
			file_type = ss.FileTypeEnum.HTML
			filename += '.html'
		else:
			file_type = ss.FileTypeEnum.CSV
			filename += ".csv"
		location = os.path.join(download_location, filename)
		continuous_filters = []
		discrete_filters = []
		if query.feature_filters:
			features = features.union(set(query.feature_filters))
		if not features or len(features) == 0:
			features = []
			include_all_columns = True
		else:
			include_all_columns = False
		for filter in query.filters:
			values = filter.values
			if type(values[0]) != str:
				for value in values:
					operatorEnum = None
					if value['operator'] is '>':
						operatorEnum = ss.OperatorEnum.GreaterThan
					elif value['operator'] is '<':
						operatorEnum = ss.OperatorEnum.LessThan
					elif value['operator'] is '<=':
						operatorEnum = ss.OperatorEnum.LessThanOrEqualTo
					elif value['operator'] is '>=':
						operatorEnum = ss.OperatorEnum.GreaterThanOrEqualTo
					elif value['operator'] is '!=':
						operatorEnum = ss.OperatorEnum.NotEquals
					elif value['operator'] is '==':
						operatorEnum = ss.OperatorEnum.Equals
					if operatorEnum:
						continuous_filters.append(ss.ContinuousQuery(filter.name, operatorEnum, value['value']))
			else:
				discrete_filters.append(ss.DiscreteQuery(filter.name, values))
		ss.exportQueryResults(self.__file, location, file_type, list(features), continuous_filters, discrete_filters,
							  includeAllColumns=include_all_columns)
		return location



	def get_sample_id_options(self) -> List:
		sample_info = ss.getColumnInfo(self.__file, SAMPLE_ID)
		return sample_info.uniqueValues

	def get_all_sample_ids(self):
		sample_info = ss.getColumnInfo(self.__file, SAMPLE_ID)
		return sample_info.uniqueValues

	def get_variable_options(self, variable_name) -> Dict[str, Any]:
		column_info = ss.getColumnInfo(self.__file, variable_name)
		if column_info.dataType == 'discrete':
			return {"numOptions": len(column_info.uniqueValues), "options": list(column_info.uniqueValues)}
		elif column_info.dataType == 'continuous':
			min_val = min(column_info.uniqueValues)
			max_val = max(column_info.uniqueValues)
			return {"min": min_val, "max": max_val, "options": "continuous"}
		else:
			return None


if __name__ == '__main__':
	dao = ParquetDao('/Volumes/KIMBALLUSB/ParquetData/LINCS_PhaseII_Level3/METABRIC.pq')
	filter_options = dao.get_variables()
	groups = {"MetaData": [], "Genes": filter_options}