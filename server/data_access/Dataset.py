#!/usr/bin/env python3
import os, json, sqlite3
from pprint import pprint
from typing import Set, List, Any, Iterable
from .Query import Query
from .Dao import ParquetDao
from .Exceptions import RequestError, ServerError
from .Constants import *
from subprocess import check_call
import pickle

import sys

METADATA_PKL = 'metadata.pkl'

class GeneyDataset:

	def __init__(self, directory: str):
		# make sure directory has a '/' at the end
		if directory[-1] is not '/':
			directory += '/'
		self.__dir = directory
		self.__id = directory.split('/')[-2]
		# make sure directory and all required files exist
		if not os.path.isdir(self.__dir):
			raise Exception('No directory "{}"'.format(self.__dir))

		for requiredFile in REQUIRED_FILES:
			if not os.path.isfile(self.__dir + requiredFile):
				raise Exception('No file ' + self.__dir + requiredFile)

		with open(self.__dir + DESCRIPTION_FILE, 'r') as in_file:
			self.__description = json.load(in_file)


	@property
	def dataset_id(self) -> str:
		return self.__id

	@property
	def directory(self) -> str:
		return self.__dir

	@property
	def num_meta_types(self) -> int:
		return self.__description['numMetaTypes']
	
	@property
	def num_features(self) -> int:
		return self.__description['numFeatures']
	
	@property
	def num_samples(self) -> int:
		return self.__description['numSamples']
	
	@property
	def description(self):
		return self.__description

	@property
	def metadata_path(self):
		return self.__dir + METADATA_PKL

	@property
	def groups_path(self):
		return self.__dir + GROUPS_JSON

	@property
	def options_path(self):
		return self.__dir + OPTIONS_JSON

	def get_variable(self, variable_name):
		with open(self.metadata_path, 'rb') as fp:
			metadata = pickle.load(fp)
			if type(metadata['meta'][variable_name]['options']) is list and len(metadata['meta'][variable_name]['options']) > 100:
				metadata['meta'][variable_name]['options'] = None
			return metadata['meta'][variable_name]

	def get_groups(self):
		with open(self.groups_path) as fp:
			groups = json.load(fp)
			for group in groups.keys():
				if len(groups[group]) > 100:
					groups[group] = None
			return groups

	def search_group(self, group_name, search_str):
		with open(self.groups_path) as fp:
			groups = json.load(fp)
			if group_name not in groups.keys():
				return []
			else:
				target_group = groups[group_name]
			if not search_str:
				return groups[group_name][:100]
			options = []
			for option in target_group:
				if search_str in option:
					options.append(option)
			return options[:100]

	def search_options(self, variable_name, search_str):
		with open(self.metadata_path, 'rb') as fp:
			metadata = pickle.load(fp)
			options = []
			if variable_name not in metadata['meta'].keys():
				return []
			if not search_str:
				return metadata['meta'][variable_name]['options'][:100]
			for option in metadata['meta'][variable_name]['options']:
				if option and search_str in option:
					options.append(option)
			return options[:100]
	# def get_filtered_data(self, filters, illegal_chars=[]):
	# 	query = Query(filters, self.__description)
	# 	sample_ids = self.query_samples(query)
	# 	meta_names = self.get_query_metatype_names(query)
	#
	# 	if SAMPLE_ID in meta_names:
	# 		meta_names.remove(SAMPLE_ID)
	#
	# 	# TODO figure out the max number of items for files we can build
	# 	feature_slices, num_features_requested = self.get_query_feature_slices(query)
	#
	# 	# TODO generate feature names rather than loading them all into memory at once
	# 	yield [SAMPLE_ID] + meta_names
	# 	yield self.get_query_feature_names(query)
	# 	yield None
	#
	# 	sqlite_dao = SQLiteDao(self.__dir)
	# 	hdf5_dao = Hdf5Dao(self.__dir)
	#
	# 	for sample_id in sample_ids:
	# 		sample_name = sqlite_dao.get_sample_name(sample_id)
	# 		sample_metadata = sqlite_dao.get_sample_metadata(sample_id, meta_names)
	# 		yield sample_name
	# 		for meta_name in meta_names:
	# 			if meta_name in sample_metadata:
	# 				if any(illegal_char in sample_metadata[meta_name] for illegal_char in illegal_chars) :
	# 					yield "\"" + sample_metadata[meta_name] + "\""
	# 				else :
	# 					yield sample_metadata[meta_name]
	# 			else:
	# 				yield ''
	#
	# 		for data_slice in hdf5_dao.get_row(sample_id, feature_slices):
	# 			yield data_slice
	# 		yield None
	#
	# 	sqlite_dao.close()
	# 	hdf5_dao.close()

	# def get_query_metatype_names(self, query: Query) -> List[str]:
	# 	if len(query.meta_filter_names):
	# 		return query.meta_filter_names
	# 	else:
	# 		with SQLiteDao(self.__dir) as dao:
	# 			return dao.get_all_variable_names()

	# returns a list of tuple pairs, where each pair represents 
	# a start and end to the slice of features to grab from the HDF5 file
	# as well as the total number of features requested
	# Example, if features 1,2,3,6,7,9 are requested, this will return ([(1,4),(6,8),(9,10)], 6)
	# def get_query_feature_slices(self, query: Query) -> Iterable[int]:
	# 	if query.feature_filters is None:
	# 		return [(0,self.num_features)], self.num_features
	# 	else:
	# 		with SQLiteDao(self.__dir) as dao:
	# 			feature_ids = sorted(dao.get_feature_ids(query.feature_filters))
	# 			feature_slices = list()
	# 			current_start = feature_ids[0]
	# 			next_number = current_start + 1
	# 			for index in range(1, len(feature_ids)):
	# 				if feature_ids[index] != next_number:
	# 					feature_slices.append((current_start, next_number))
	# 					current_start = feature_ids[index]
	# 				next_number = feature_ids[index] + 1
	# 			feature_slices.append((current_start, next_number))
	# 		return feature_slices, len(feature_ids)
	#
	# def get_query_feature_names(self, query: Query) -> str:
	# 	if query.feature_filters is None:
	# 		with SQLiteDao(self.__dir) as dao:
	# 			return dao.get_all_feature_names()
	# 	else:
	# 		return query.feature_filters

	def get_num_samples_matching_filters(self, filters) -> int:
		try:
			query = Query(filters, self.__description)
			if query.num_filters > 0:
				return len(self.query_samples(query))
			else:
				return self.num_samples
		except RequestError:
			return None

	# returns set of sample ids that match filters
	def query_samples(self, query: Query):
		with ParquetDao(self.__dir) as dao:
			if query.num_filters > 0: # if they added any filters
				return set(dao.get_samples_from_query(query))
			else: # they added no filters so all sample ids "match"
				return set(dao.get_all_sample_ids())

	def query(self, query_json, file_format, gzip_output, download_location):
		query = Query(query_json, self.description)
		with ParquetDao(self.__dir) as dao:
			file_path = dao.get_file_from_query(query, file_format, self.dataset_id, download_location)
			if gzip_output:
				check_call(['gzip', file_path])
				file_path += ".gz"
			return file_path


	# def search(self, meta_type, search_val):
	# 	with SQLiteDao(self.__dir) as dao:
	# 		if meta_type == '':
	# 			meta_types = dao.search_meta_types(search_val)
	# 			if search_val == '' or search_val in 'sampleID':
	# 				meta_types.insert(0, 'sampleID')
	# 			return meta_types
	# 		elif meta_type == 'features':
	# 			return dao.search_features(search_val)
	# 		elif meta_type == SAMPLE_ID:
	# 			return dao.search_sample_id(search_val)
	# 		else:
	# 			return dao.search_meta_type(meta_type, search_val)

if __name__ == '__main__':
	dset = GeneyDataset("/Volumes/KIMBALLUSB/ParquetData/LINCS_PhaseII_Level3/")
	results = dset.get_variable("1-Mar")
	print(results)
