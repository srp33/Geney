import json
import io
import csv
import msgpack
import pandas as pd
from shapeshifter.files import SSFile
import time


class GeneyQuery:
	"""
	Represents and handles queries stored by Geney as JSON file
	"""

	def __init__(self, geney_file_collection, json_filter):
		"""
		Initializes GeneyQuery object.
		self.filters is a dictionary mapping column names to lists containing either a dictionary or lists of values
		self.features is a list of additional columns to include in the output
		self.groups is a list with strings, where if any column starts with any of these values plus a double
			underscore, it should be included in the output
		self.geney_file_collection is a GeneyFileCollection object with all necessary files to perform filters
		"""
		#        with open(geney_file_collection.json_file) as f:
		#            data = json.load(f)
		data = json.loads(json_filter)
		self.filters = data["filters"]
		self.features = data["features"]
		self.groups = data["groups"]
		self.geney_file_collection = geney_file_collection

	@staticmethod
	def write_to_file(df, out_file_path, out_file_type=None, gzip_results=False, include_index=False, null='NA',
					  index_col="Sample", transpose=False):
		start = time.time()
		output_file = SSFile.factory(out_file_path, out_file_type)
		output_file.write_to_file(df, gzipResults=gzip_results, includeIndex=include_index, null=null,
								  indexCol=index_col, transpose=transpose)
		end = time.time()
		print('Time to write to file: {:.2}s'.format(end-start), flush=True)
		return out_file_path

	def filter_data(self, samples_only=False):
		start = time.time()
		indexes_sets = []
		for single_filter in self.filters:
			if self.__determine_filter_type(self.filters[single_filter]) == "discrete":
				indexes_sets.append(self.__perform_discrete_filter(single_filter, self.filters[single_filter]))
			elif self.__determine_filter_type(self.filters[single_filter]) == "continuous":
				indexes_sets.append(self.__perform_continuous_filter(single_filter, self.filters[single_filter]))
			else:
				raise Exception("Error: JSON query is malformed")
		end = time.time()
		print('T1: {:.2f}s'.format(end - start), flush=True)
		start = time.time()

		# Find intersection of all sets produced by filters
		result_row_indexes = set.intersection(*indexes_sets)
		result_row_indexes = sorted(list(result_row_indexes))
		# Grab rows that match the indexes
		matching_samples = []
		for index in result_row_indexes:
			matching_samples.append(self.geney_file_collection.samples[index])
		if samples_only:
			return matching_samples
		end = time.time()
		print('T2: {:.2f}s'.format(end - start), flush=True)
		start = time.time()

		# Determine which columns (specifically the indexes) to grab for all the matching samples
		desired_column_indexes = self.__determine_additional_columns()
		desired_column_indexes.insert(0, 0)
		output_rows = []
		header_row = [self.geney_file_collection.features[i].decode('UTF-8') for i in desired_column_indexes]
		output_rows.append(header_row)
		del (desired_column_indexes[0])
		end = time.time()
		print('T3: {:.2f}s'.format(end - start), flush=True)
		start = time.time()

		# TODO: add an option for grabbing all items in the row, not just the desired columns?
		for sample in matching_samples:
			self.geney_file_collection.tsv_file.seek(self.geney_file_collection.tsv_map[sample][0])
			entire_row = self.geney_file_collection.tsv_file.read(self.geney_file_collection.tsv_map[sample][1]).rstrip(
				b"\n").split(b"\t")
			reduced_row = [sample] + [entire_row[i - 1] for i in desired_column_indexes]
			reduced_row = (b"\t".join(reduced_row)).decode('UTF-8')
			reduced_row = reduced_row.split("\t")
			output_rows.append(reduced_row)

		end = time.time()
		print('T4: {:.2f}s'.format(end - start), flush=True)
		start = time.time()
		df = self.__build_pandas_dataframe(output_rows)
		end = time.time()
		print('Time to build pandas dataframe: {:.2f}s'.format(end-start), flush=True)
		return df

	def __build_pandas_dataframe(self, output_rows):
		output = io.StringIO()
		csv_writer = csv.writer(output, delimiter='\t')
		for row in output_rows:
			csv_writer.writerow(row)
		output.seek(0)
		df = pd.read_csv(output, sep='\t')
		return df

	def __write_to_csv(self, output_rows):
		out = open("output.tsv", "w")
		for row in output_rows:
			out.write(row)

	def __determine_additional_columns(self):
		"""
		Finds the indexes of all columns whose data will be reported.
		This includes columns specified in the filters, the features, and the groups
		"""
		# Start with additional requested features
		column_indexes = [i for i in range(0, len(self.geney_file_collection.features))
						  if (self.geney_file_collection.features[i].decode("UTF-8") in self.features)]
		# Add features mentioned in the filters
		filter_columns = [key for key in self.filters]
		filter_column_indexes = [i for i in range(0, len(self.geney_file_collection.features))
								 if (self.geney_file_collection.features[i].decode("UTF-8") in filter_columns)]
		column_indexes += filter_column_indexes
		# Add features determined by groups
		column_indexes += self.__determine_group_columns()
		column_indexes = sorted(list(set(column_indexes)))
		return column_indexes

	def __determine_group_columns(self):
		"""
		Finds column names that start with whatever is listed under self.groups plus a double underscore.
		Returns the index of those columns
		"""

		columns_from_group = []
		for group in self.groups:
			temp_columns = [feature for feature in self.geney_file_collection.features if
							(feature.decode("UTF-8").startswith(group + "__"))]
			columns_from_group += temp_columns

		# get indexes of the columns
		group_indexes = [i for i in range(0, len(self.geney_file_collection.features))
						 if (self.geney_file_collection.features[i] in columns_from_group)]
		return group_indexes

	def __determine_filter_type(self, single_filter):

		if isinstance(single_filter[0], dict):
			return "continuous"
		elif isinstance(single_filter[0], str) or isinstance(single_filter, bool):
			return "discrete"
		else:
			print(single_filter)
			raise Exception("Error: JSON filter is malformed")

	def __perform_discrete_filter(self, column_name, values_list):
		"""
		Performs a filter for discrete values
		:param column_name: string name of a column to be examined
		:param values_list: list of string values that are accepted in the column of 'column_name'
		:return: set with row indexes of rows that match filter criteria
		"""
		location_range = self.geney_file_collection.transposed_map[bytes(column_name, encoding='utf-8')]
		self.geney_file_collection.transposed_tsv_file.seek(location_range[0])
		desired_feature_data = self.geney_file_collection.transposed_tsv_file.read(location_range[1]).split(b"\t")
		matching_samples = [item for item in range(0, len(desired_feature_data)) if
							(desired_feature_data[item].decode("UTF-8") in values_list)]
		return set(matching_samples)

	def __perform_continuous_filter(self, column_name, filter_info):
		"""
		Performs a filter for continuous values
		:param column_name: string name of a column to be examined
		:param filter_info: list with a dictionary with key "operator" whose value is a string representation of a mathematcial operator,
			and a key "value" with a numerical value
		:return: set with row indexes of rows that match filter criteria
		"""
		# TODO: find out how to fix the line below, converting column_name to b
		location_range = self.geney_file_collection.transposed_map[bytes(column_name, encoding='utf-8')]
		self.geney_file_collection.transposed_tsv_file.seek(location_range[0])
		desired_feature_data = self.geney_file_collection.transposed_tsv_file.read(location_range[1]).split(b"\t")
		# matching_samples holds the indexes of samples that match the filters
		matching_samples = []
		operator = filter_info[0]["operator"]
		value = filter_info[0]["value"]
		if operator == "<":
			matching_samples = [item for item in range(0, len(desired_feature_data))
								if (desired_feature_data[item] != b'NA' and float(desired_feature_data[item]) < value)]
		elif operator == "<=":
			matching_samples = [item for item in range(0, len(desired_feature_data))
								if (desired_feature_data[item] != b'NA' and float(desired_feature_data[item]) <= value)]
		elif operator == ">":
			matching_samples = [item for item in range(0, len(desired_feature_data))
								if (desired_feature_data[item] != b'NA' and float(desired_feature_data[item]) > value)]
		elif operator == ">=":
			matching_samples = [item for item in range(0, len(desired_feature_data))
								if (desired_feature_data[item] != b'NA' and float(desired_feature_data[item]) >= value)]
		elif operator == "==":
			matching_samples = [item for item in range(0, len(desired_feature_data))
								if (desired_feature_data[item] != b'NA' and float(desired_feature_data[item]) == value)]
		elif operator == "!=":
			matching_samples = [item for item in range(0, len(desired_feature_data))
								if (desired_feature_data[item] != b'NA' and float(desired_feature_data[item]) != value)]
		else:
			raise Exception("Error: invalid operator in JSON filter: " + str(operator))
		return set(matching_samples)


class GeneyFileCollection:
	"""
	Stores all TSV and MessagePack file information needed allow for future filtering
	"""

	def __init__(self, tsv_file_path, messagepack_tsv_path, transposed_tsv_file_path,
				 transposed_messagepack_tsv_path):
		messagepack_tsv = open(messagepack_tsv_path + "/sample_data.msgpack", "rb")
		self.tsv_map = msgpack.unpack(messagepack_tsv)
		sample_file = open(messagepack_tsv_path + "/samples.msgpack", "rb")
		self.samples = msgpack.unpack(sample_file)
		transposed_map_file = open(transposed_messagepack_tsv_path + "/sample_data.msgpack", "rb")
		self.transposed_map = msgpack.unpack(transposed_map_file)
		transposed_samples_file = open(transposed_messagepack_tsv_path + "/samples.msgpack", "rb")
		self.transposed_samples = msgpack.unpack(transposed_samples_file)
		self.tsv_file = open(tsv_file_path, "rb")
		self.transposed_tsv_file = open(transposed_tsv_file_path, "rb")
		features_file = open(messagepack_tsv_path + "/features.msgpack", "rb")
		self.features = msgpack.unpack(features_file)
