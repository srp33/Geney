#!/usr/bin/env python3
import os
from .Exceptions import RequestError
from .Constants import *
from .Query import *
import pickle
import uuid


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

		for dir in [DATA_MP, TRANSPOSED_MP]:
			if not os.path.isdir(self.__dir + dir):
				raise Exception('No message pack directory {}'.format(dir))

		with open(self.__dir + DESCRIPTION_FILE, 'r') as in_file:
			self.__description = json.load(in_file)

	@property
	def dataset_id(self) -> str:
		return self.__id

	@property
	def directory(self) -> str:
		return self.__dir

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

	def get_variable(self, variable_name):
		variable_name = bytes(variable_name, encoding='ascii')
		with open(self.metadata_path, 'rb') as fp:
			metadata = pickle.load(fp)
			if type(metadata['meta'][variable_name]['options']) is list and len(
					metadata['meta'][variable_name]['options']) > 100:
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
		variable_name = bytes(variable_name, encoding='ascii')
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

	def get_num_samples_matching_filters(self, query_json) -> int:
		try:
			query_dict = json.loads(query_json)
			if query_dict['filters'] != {}:
				return len(self.query_samples(query_json))
			else:
				return self.num_samples
		except RequestError:
			return None

	def get_num_data_points(self, num_samples, selected_groups, selected_features):
		num_data_points = len(selected_features)
		with open(self.groups_path) as fp:
			groups = json.load(fp)
			for group in selected_groups:
				num_data_points += len(groups[group])
		num_data_points *= num_samples
		return int(num_data_points)

	# returns set of sample ids that match filters
	def query_samples(self, query_json):
		query_object = GeneyQuery(self.get_file_collection(), query_json)
		return query_object.filter_data(samples_only=True)

	def query(self, query_json, file_format, gzip_output, download_location, filename=None):
		if not filename:
			filename = '{}{}.{}'.format(self.__id, uuid.uuid4().hex[:8], file_format)
		filename += 'incomplete'
		out_file_path = os.path.join(download_location, filename)
		query_object = GeneyQuery(self.get_file_collection(), query_json)
		data = query_object.filter_data()
		file_path = query_object.write_to_file(data, out_file_path, file_format, gzip_results=gzip_output)
		os.rename(file_path, file_path.rstrip('incomplete'))
		return file_path.rstrip('incomplete')

	def get_file_collection(self):
		data_file = self.__dir + DATA_FILE
		transposed_data_file = self.__dir + TRANSPOSED_DATA_FILE
		data_mp = self.__dir + DATA_MP
		transposed_mp = self.__dir + TRANSPOSED_MP
		return GeneyFileCollection(data_file, data_mp, transposed_data_file, transposed_mp)
