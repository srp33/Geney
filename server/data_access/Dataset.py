#!/usr/bin/env python3
import os, json, sqlite3
from pprint import pprint
from typing import Set, List, Any, Iterable
from .Query import Query
from .Dao import SQLiteDao, Hdf5Dao
from .Exceptions import RequestError, ServerError
from .Constants import *

import sys

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
		print(self.__id)
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
	def description(self):
		return self.__description

	@property
	def metadata_path(self):
		return self.__dir + METADATA_JSON

	def get_variable(self, variable_name):
		with SQLiteDao(self.__dir) as dao:
			return dao.get_variable_options(variable_name)

	def get_filtered_data(self, filters, illegal_chars=[]):
		query = Query(filters, self.__description)
		sample_ids = self.query_samples(query)
		meta_names = self.get_query_metatype_names(query)

		if SAMPLE_ID in meta_names:
			meta_names.remove(SAMPLE_ID)
		print(meta_names)

		# TODO figure out the max number of items for files we can build
		feature_slices, num_features_requested = self.get_query_feature_slices(query)

		# TODO generate feature names rather than loading them all into memory at once
		yield [SAMPLE_ID] + meta_names
		yield self.get_query_feature_names(query)
		yield None

		sqlite_dao = SQLiteDao(self.__dir)
		hdf5_dao = Hdf5Dao(self.__dir)

		for sample_id in sample_ids:
			sample_name = sqlite_dao.get_sample_name(sample_id)
			sample_metadata = sqlite_dao.get_sample_metadata(sample_id, meta_names)
			yield sample_name
			for meta_name in meta_names:
				if meta_name in sample_metadata:
					yield sample_metadata[meta_name]
				else:
					yield ''

			for data_slice in hdf5_dao.get_row(sample_id, feature_slices):
				yield data_slice
			yield None

		sqlite_dao.close()
		hdf5_dao.close()


	def get_query_metatype_names(self, query: Query) -> List[str]:
		if len(query.meta_filter_names):
			return query.meta_filter_names
		else:
			with SQLiteDao(self.__dir) as dao:
				return dao.get_all_variable_names()
	# returns a list of tuple pairs, where each pair represents 
	# a start and end to the slice of features to grab from the HDF5 file
	# as well as the total number of features requested
	# Example, if features 1,2,3,6,7,9 are requested, this will return ([(1,4),(6,8),(9,10)], 6)
	def get_query_feature_slices(self, query: Query) -> Iterable[int]:
		if query.feature_filters is None:
			return [(0,self.num_features)], self.num_features
		else:
			with SQLiteDao(self.__dir) as dao:
				feature_ids = sorted(dao.get_feature_ids(query.feature_filters))
				feature_slices = list()
				current_start = feature_ids[0]
				next_number = current_start + 1
				for index in range(1, len(feature_ids)):
					if feature_ids[index] != next_number:
						feature_slices.append((current_start, next_number))
						current_start = feature_ids[index]
					next_number = feature_ids[index] + 1
				feature_slices.append((current_start, next_number))
			return feature_slices, len(feature_ids)

	def get_query_feature_names(self, query: Query) -> str:
		if query.feature_filters is None:
			with SQLiteDao(self.__dir) as dao:
				return dao.get_all_feature_names()
		else:
			return query.feature_filters

	def get_num_samples_matching_filters(self, filters) -> int:
		return len(self.query_samples(Query(filters, self.__description)))

	# returns set of sample ids that match filters
	def query_samples(self, query: Query) -> Set[int]:
		sample_ids = None
		with SQLiteDao(self.__dir) as dao:
			for meta_filter in query.meta_filters:
				if meta_filter.name == SAMPLE_ID:
					matched = dao.get_sample_ids(meta_filter.values)
				else:
					matched = dao.get_samples_matching_filter(meta_filter)
				# if any one filter has no matches, there is no point in continuing to search
				if len(matched) == 0:
					return frozenset()
				# if this if the first filter queried, it starts off our set
				if sample_ids is None:
					sample_ids = matched
				else: # otherwise get the intersection of all matched sample ids
					sample_ids.intersection_update(matched)
					# if no sample ids match filters, we're done
					if len(sample_ids) == 0:
						return frozenset()
		return frozenset(sample_ids)

	def search(self, meta_type, search_val):
		with SQLiteDao(self.__dir) as dao:
			if meta_type == '':
				return dao.search_meta_types(search_val)
			elif meta_type == 'features':
				return dao.search_features(search_val)
			elif meta_type == SAMPLE_ID:
				return dao.search_sample_id(search_val)
			else:
				print("SEARCHING META TYPE", meta_type)
				return dao.search_meta_type(meta_type, search_val)

		
if __name__ == '__main__':
	dataset = GeneyDataset('/Users/pjtatlow/projects/web/geney/data/mRNA_CCLE_isoform/')
	# pprint(dataset.metadata)

	filters = {
		'meta': {
			'Histology': ["carcinoma"],
			'Hist Subtype1': ['small_cell_carcinoma']
		},
		'features': ['ENST00000000233.9','ENST00000042381.8', 'ENST00000215368.3', 'ENST00000219789.10', 'ENST00000497803.1', 'ENST00000534252.2', 'ENST00000576964.5', 'ENST00000621460.1'],
		# 'features': [],
	}
	rows = -1
	for text in dataset.filter_data(filters):
		rows += 1
		sys.stderr.write(text)
		sys.stderr.flush()
		# print('WROTE ROW', rows)