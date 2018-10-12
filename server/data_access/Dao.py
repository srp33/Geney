# import h5py
# from typing import List, Dict, Any
#
# import UseParquet as ss
# from .Constants import *
# from .Query import Query
# import os
# import uuid
#
#
# class Hdf5Dao:
# 	def __init__(self, directory):
# 		self.__hdf5 = h5py.File(directory + DATA_FILE, 'r')
# 		self.__data = self.__hdf5[HDF5_DATA_PATH]
#
# 	def get_row(self, row_index, col_indices) -> List[str]:
# 		for start, end in col_indices:
# 			yield self.__data[row_index, start:end].astype(str)
#
# 	def close(self):
# 		self.__hdf5.close()
#
#
# class ParquetDao:
# 	def __init__(self, directory):
# 		# self.__file = directory
# 		self.__file = "{}{}".format(directory, DATA_FILE)
#
# 	def __enter__(self):
# 		return self
#
# 	def __exit__(self, exc_type, exc_val, exc_tb):
# 		return exc_val
#
# 	def get_variables(self):
# 		return ss.getColumnNames(self.__file)
#
# 	def get_samples_from_query(self, query: Query):
# 		continuous_filters = []
# 		discrete_filters = []
# 		for filter in query.filters:
# 			values = filter.values
# 			if type(values[0]) != str:
# 				for value in values:
# 					operatorEnum = None
# 					if value['operator'] is '>':
# 						operatorEnum = ss.OperatorEnum.GreaterThan
# 					elif value['operator'] is '<':
# 						operatorEnum = ss.OperatorEnum.LessThan
# 					elif value['operator'] is '<=':
# 						operatorEnum = ss.OperatorEnum.LessThanOrEqualTo
# 					elif value['operator'] is '>=':
# 						operatorEnum = ss.OperatorEnum.GreaterThanOrEqualTo
# 					elif value['operator'] is '!=':
# 						operatorEnum = ss.OperatorEnum.NotEquals
# 					elif value['operator'] is '==':
# 						operatorEnum = ss.OperatorEnum.Equals
# 					if operatorEnum:
# 						continuous_filters.append(ss.ContinuousQuery(filter.name, operatorEnum, value['value']))
# 			else:
# 				discrete_filters.append(ss.DiscreteQuery(filter.name, values))
# 		df = ss.query(self.__file, discreteQueries=discrete_filters, continuousQueries=continuous_filters)
# 		return df.index.values
#
# 	def get_file_from_query(self, query: Query, features, file_format, dataset_id, download_location, filename=None):
# 		if not filename:
# 			filename = dataset_id + uuid.uuid4().hex[:8]
# 		filename += 'incomplete'
# 		if file_format == 'csv':
# 			file_type = ss.FileTypeEnum.CSV
# 		elif file_format == 'json':
# 			file_type = ss.FileTypeEnum.JSON
# 		elif file_format == 'pickle':
# 			file_type = ss.FileTypeEnum.Pickle
# 		elif file_format == 'tsv':
# 			file_type = ss.FileTypeEnum.TSV
# 		elif file_format == 'hdf5':
# 			file_type = ss.FileTypeEnum.HDF5
# 		elif file_format == 'arff':
# 			file_type = ss.FileTypeEnum.ARFF
# 		elif file_format == 'excel':
# 			file_type = ss.FileTypeEnum.Excel
# 		elif file_format == 'feather':
# 			file_type = ss.FileTypeEnum.Feather
# 		elif file_format == 'msgpack':
# 			file_type = ss.FileTypeEnum.MsgPack
# 		elif file_format == 'parquet':
# 			file_type = ss.FileTypeEnum.Parquet
# 		elif file_format == 'stata':
# 			file_type = ss.FileTypeEnum.Stata
# 		elif file_format == 'sqlite':
# 			file_type = ss.FileTypeEnum.SQLite
# 		elif file_format == 'html':
# 			file_type = ss.FileTypeEnum.HTML
# 		else:
# 			file_type = ss.FileTypeEnum.CSV
# 		location = os.path.join(download_location, filename)
# 		continuous_filters = []
# 		discrete_filters = []
# 		if query.feature_filters:
# 			features = features.union(set(query.feature_filters))
# 		if not features or len(features) == 0:
# 			features = []
# 			include_all_columns = True
# 		else:
# 			include_all_columns = False
# 		for filter in query.filters:
# 			values = filter.values
# 			if type(values[0]) != str:
# 				for value in values:
# 					operatorEnum = None
# 					if value['operator'] is '>':
# 						operatorEnum = ss.OperatorEnum.GreaterThan
# 					elif value['operator'] is '<':
# 						operatorEnum = ss.OperatorEnum.LessThan
# 					elif value['operator'] is '<=':
# 						operatorEnum = ss.OperatorEnum.LessThanOrEqualTo
# 					elif value['operator'] is '>=':
# 						operatorEnum = ss.OperatorEnum.GreaterThanOrEqualTo
# 					elif value['operator'] is '!=':
# 						operatorEnum = ss.OperatorEnum.NotEquals
# 					elif value['operator'] is '==':
# 						operatorEnum = ss.OperatorEnum.Equals
# 					if operatorEnum:
# 						continuous_filters.append(ss.ContinuousQuery(filter.name, operatorEnum, value['value']))
# 			else:
# 				discrete_filters.append(ss.DiscreteQuery(filter.name, values))
# 		ss.exportQueryResults(self.__file, location, file_type, list(features), continuous_filters, discrete_filters,
# 							  includeAllColumns=include_all_columns)
# 		return location
#
# 	def get_sample_id_options(self) -> List:
# 		sample_info = ss.getColumnInfo(self.__file, SAMPLE_ID)
# 		return sample_info.uniqueValues
#
# 	def get_all_sample_ids(self):
# 		sample_info = ss.getColumnInfo(self.__file, SAMPLE_ID)
# 		return sample_info.uniqueValues
#
# 	def get_variable_options(self, variable_name) -> Dict[str, Any]:
# 		column_info = ss.getColumnInfo(self.__file, variable_name)
# 		if column_info.dataType == 'discrete':
# 			return {"numOptions": len(column_info.uniqueValues), "options": list(column_info.uniqueValues)}
# 		elif column_info.dataType == 'continuous':
# 			min_val = min(column_info.uniqueValues)
# 			max_val = max(column_info.uniqueValues)
# 			return {"min": min_val, "max": max_val, "options": "continuous"}
# 		else:
# 			return None
#
#
# if __name__ == '__main__':
# 	dao = ParquetDao('/Volumes/KIMBALLUSB/ParquetData/LINCS_PhaseII_Level3/METABRIC.pq')
# 	filter_options = dao.get_variables()
# 	groups = {"MetaData": [], "Genes": filter_options}
