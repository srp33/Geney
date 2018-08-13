#!/usr/bin/env python3
import os, json, sqlite3
from pprint import pprint
from typing import Set, List, Any, Iterable
from .Query import Query
from .Dao import ParquetDao
from .Exceptions import RequestError, ServerError
from .Constants import *
from subprocess import check_call
import gzip
from shutil import copyfileobj
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

	def query(self, query_json, file_format, gzip_output, download_location, filename=None):
		query = Query(query_json, self.description)
		features = []
		if query.groups:
			with open(self.groups_path) as fp:
				groups = json.load(fp)
				for group in query.groups:
					features.extend(groups[group])
		with ParquetDao(self.__dir) as dao:
			file_path = dao.get_file_from_query(query, set(features), file_format, self.dataset_id, download_location, filename)
			with open(file_path, 'rb') as f_in:
				if gzip_output:
					with gzip.open(file_path.rstrip('incomplete'), 'wb') as f_out:
						copyfileobj(f_in, f_out)
				else:
					with open(file_path.rstrip('incomplete'), 'wb') as f_out:
						copyfileobj(f_in, f_out)
				os.remove(file_path)
			print('Done!', flush=True)
			return file_path.rstrip('incomplete')


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
