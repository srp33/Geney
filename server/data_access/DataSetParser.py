import fastnumbers
import glob
from itertools import islice
import mmap
import operator
import os
import sys
from data_access.DataSetHelper import *
from data_access.filters import DiscreteFilter, NumericFilter


class DataSetParser:
    def __init__(self, data_file_path):
        self.data_file_path = data_file_path

        self.__id = None
        self.__timestamp = None
        self.__description = None
        self.__featureDescription = None
        self.__featureDescriptionPlural = None
        self.__title = None
        self.__num_samples = None
        self.__num_features = None
        self.__total_data_points = None

    @property
    def id(self) -> str:
        if self.__id is None:
            self.__id = readStringFromFile(self.data_file_path, ".id").decode()
        return self.__id

    @property
    def timestamp(self) -> float:
        if self.__timestamp is None:
            self.__timestamp = float(readStringFromFile(self.data_file_path, ".timestamp").decode())
        return self.__timestamp

    @property
    def title(self) -> str:
        if self.__title is None:
            self.__title = readStringFromFile(self.data_file_path, ".title").decode()
        return self.__title

    @property
    def description(self) -> str:
        if self.__description is None:
            self.__description = readStringFromFile(self.data_file_path, ".description").decode()
        return self.__description

    @property
    def num_samples(self) -> int:
        if self.__num_samples is None:
            self.__num_samples = readIntFromFile(self.data_file_path, ".nrow")
        return self.__num_samples

    @property
    def num_features(self) -> int:
        if self.__num_features is None:
            self.__num_features = readIntFromFile(self.data_file_path, ".ncol")
        return self.__num_features

    @property
    def info(self) -> dict:
        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'uploadDate': self.timestamp,
            'numSamples': self.num_samples,
            'numFeatures': self.num_features
        }

    @property
    def total_datapoints(self):
        if self.__total_data_points is None:
            self.__total_data_points = self.num_samples * self.num_features
        return self.__total_data_points

    # This function accepts filtering criteria, saves the matching row indices to a file,
    #   and returns the number of matching samples as well as the path to that file.
    # The input arguments must be of type DiscreteFilter or NumericFilter, respectively.
    # Make sure to delete the temp file after you are done with it!
    def save_sample_indices_matching_filters(self, discrete_filters, numeric_filters):
        # Prepare to parse data
        data_handle = openReadFile(self.data_file_path)
        ll = readIntFromFile(self.data_file_path, ".ll")
        cc_handle = openReadFile(self.data_file_path, ".cc")
        mccl = readIntFromFile(self.data_file_path, ".mccl")
        num_rows = self.num_samples

        # Read the column names
        all_column_names = get_column_names(self.data_file_path)

        # Find rows that match discrete filtering criteria
        keep_row_indices = range(num_rows)
        for df in discrete_filters:
            keep_row_indices = self.filter_rows_discrete(keep_row_indices, df, data_handle, cc_handle, mccl, ll)

        # Find rows that match numeric filtering criteria
        num_operator_dict = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le, "==": operator.eq, "!=": operator.ne}
        for nf in numeric_filters:
            keep_row_indices = self.filter_rows_numeric(keep_row_indices, nf, num_operator_dict, data_handle, cc_handle, mccl, ll)

        # Save the row indices to a file
        keep_row_indices = [str(x).encode() for x in keep_row_indices]
        temp_file_path = self.generate_temp_file_path()
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(b"\n".join(keep_row_indices))

        data_handle.close()
        cc_handle.close()

        return len(keep_row_indices), temp_file_path

    # This function identifies which columns should be selected based on the specified
    #   columns, groups, and pathways. It returns the number of columns to be selected,
    #   a file path that contains the indices of the selected columns, and a file path
    #   that contains the names of the selected columns (in that order).
    # The input arguments should be lists of strings. If all the lists are empty, then
    #   all columns will be selected.
    # Make sure to delete the temp file after you are done with it!
    def save_column_indices_to_select(self, select_columns, select_groups, select_pathways):
        # Read the column names
        column_names = list(readStringsFromFile(self.data_file_path, ".cn"))

        # By default, select all columns
        if len(select_columns) == 0 and len(select_groups) == 0 and len(select_pathways) == 0:
            select_column_indices = range(len(column_names))
        else:
            select_column_indices = set([0] + select_columns)

            # Parse pathways and add corresponding genes to the list of columns that will be selected
            select_column_indices = select_column_indices | self.parse_indices_for_groups(".pathways", select_pathways)

            # Find which columns to select based on groups
            select_column_indices = select_column_indices | self.parse_indices_for_groups(".groups", select_groups)

        select_column_indices = sorted(list(select_column_indices))

        # Save the column indices to a file
        temp_file_path_indices = self.generate_temp_file_path()
        with open(temp_file_path_indices, "wb") as temp_file:
            temp_file.write(b"\n".join([str(i).encode() for i in select_column_indices]))

        # Save the column names to a file
        temp_file_path_names = self.generate_temp_file_path()
        with open(temp_file_path_names, "wb") as temp_file:
            temp_file.write(b"\t".join([column_names[i] for i in select_column_indices]))

        return len(select_column_indices), temp_file_path_indices, temp_file_path_names

    # This function retrieves data for the specified rows and columns and builds
    #   a file with the data. The first two arguments should be paths to files created
    #   using the above functions. The third argument indicates the path where the
    #   output file will be saved. The fourth argument is the type/format of the output file.
    # This function does not return anything.
    #### NOTE: Temporarily, tsv is the only supported option for the output file type.
    def build_output_file(self, row_indices_file_path, col_indices_file_path, col_names_file_path, out_file_path, out_file_type):
        row_indices = []
        if os.path.getsize(row_indices_file_path) > 0:
            row_indices = readIntsFromFile(row_indices_file_path)

        # This is a generator
        col_indices = readIntsFromFile(col_indices_file_path)

        # Prepare to parse data
        data_handle = openReadFile(self.data_file_path)
        ll = readIntFromFile(self.data_file_path, ".ll")
        cc_handle = openReadFile(self.data_file_path, ".cc")
        mccl = readIntFromFile(self.data_file_path, ".mccl")

        # Get the coords for each column to select
        select_column_coords = list(parse_data_coords(col_indices, cc_handle, mccl))

        # Write output file (in chunks)
        with open(out_file_path, 'wb') as out_file:
            # Header line
            out_file.write(readStringFromFile(col_names_file_path) + b"\n")

            out_lines = []
            chunk_size = 1000

            for row_index in row_indices:
                out_lines.append(b"\t".join([x.rstrip() for x in parse_data_values(row_index, ll, select_column_coords, data_handle)]))

                if len(out_lines) % chunk_size == 0:
                    out_file.write(b"\n".join(out_lines) + b"\n")
                    out_lines = []

            if len(out_lines) > 0:
                out_file.write(b"\n".join(out_lines) + b"\n")

        data_handle.close()
        cc_handle.close()

    # This is a convenience function, which acts as a wrapper around other functions.
    def query(self, discrete_filters, numeric_filters, select_columns, select_groups, select_pathways, out_file_path, out_file_type="tsv"):
        num_samples, row_indices_file_path = self.save_sample_indices_matching_filters(discrete_filters, numeric_filters)
        num_columns, col_indices_file_path, col_names_file_path = self.save_column_indices_to_select(select_columns, select_groups, select_pathways)

        self.build_output_file(row_indices_file_path, col_indices_file_path, col_names_file_path, out_file_path, out_file_type)

        if os.path.exists(row_indices_file_path):
            os.remove(row_indices_file_path)
        if os.path.exists(col_indices_file_path):
            os.remove(col_indices_file_path)

        return num_samples, num_columns

    # This function returns a dictionary where each key is a group name and
    #   each value is a list of tuples. Each tuple will indicate the index of
    #   a feature and the actual feature name. If a group has more than
    #   the maximum number of elements, the value will be None. We will obtain
    #   these values later using search_group().
    def get_groups(self, max_num=100):
        group_dict = {}
        file_extension = ".groups"

        if os.path.exists(self.data_file_path + file_extension):
            the_file = openReadFile(self.data_file_path, file_extension)
            for line in iter(the_file.readline, b""):
                line_items = line.rstrip(b"\n").split(b"\t")
                group_name = line_items[0].decode()

                group_values = self.parse_comma_values(line_items[1].decode(), line_items[2].decode(), None, max_num)
                if len(group_values) > max_num:
                    group_values = None
                group_dict[group_name] = group_values

            the_file.close()

        return group_dict

    # This function returns a list of tuples. Each tuple will indicate the index of
    #   a feature and the actual feature name. If a group has more than
    #   the maximum number of elements, this function will the maximum number.
    def search_group(self, group_name, search_str=None, max_num=100):
        return self.parse_values_for_group(".groups", group_name, search_str, max_num)

    # This function returns a list of tuples. The first element in each tuple is the
    #   name of a pathway. The second element in each tuple is the number of genes in
    #   that pathway for this dataset. Each dataset may have different pathways.
    def get_pathways(self):
        pathways = []
        file_extension = ".pathways"

        if os.path.exists(self.data_file_path + file_extension):
            the_file = openReadFile(self.data_file_path, file_extension)

            for line in iter(the_file.readline, b""):
                line_items = line.rstrip(b"\n").split(b"\t")
                pathways.append((line_items[0].decode(), len(line_items[1].split(b","))))

            the_file.close()

        return pathways

    # This function returns metadata for a given variable. If it is a numeric
    #   variable, it returns the min and max values. If it is a discrete
    #   variable, it returns the list of options (or None if there are too many).
    def get_variable_meta(self, column_index, max_discrete_options=100):
        description_raw = self.get_variable_description(column_index)
        description_parts = description_raw.split("|")

        if len(description_parts) == 1:  # It is a numeric variable
            min_max = [float(x) for x in description_parts[0].split(",")]
            return {
                'min': min_max[0],
                'max': min_max[1],
                'options': 'continuous'
            }

        if description_parts[1] == "ID":
            discrete_options = list(islice(self.search_id(column_index), max_discrete_options + 1))
        else:
            discrete_options = list(islice(self.isplit(description_parts[1], ","), max_discrete_options + 1))

        if len(discrete_options) > max_discrete_options:
            return {
                'numOptions': int(description_parts[0]),
                'options': None
            }

        return {
            'numOptions': int(description_parts[0]),
            'options': discrete_options
        }

    # This function returns options for the specified discrete variable.
    # Note: If you search for options for the Sample column, it will just return "ID".
    def search_variable_options(self, column_index, search_str, max_discrete_options=100):
        description_raw = self.get_variable_description(column_index)
        description_parts = description_raw.split("|")

        if description_parts[1] == "ID":
            matches = islice(self.search_id(column_index), max_discrete_options + 1)

            if search_str:
                matches = islice(self.search_id(column_index, search_str), max_discrete_options + 1)
        else:
            matches = (x for x in self.isplit(description_parts[1], ","))

            if search_str:
                matches = (x for x in self.isplit(description_parts[1], ",") if search_str in x)

        return list(islice(matches, max_discrete_options))

    # For now, this function is a bit of a hack (for lack of a better idea).
    #   It looks through the temp directory and deletes any file that is older
    #   than 15 minutes. It returns the number of files that were deleted.
    def clean_up(self, max_age_seconds=900):
        temp_dir_path = self.get_temp_dir_path()

        num_deleted = 0

        if os.path.exists(temp_dir_path):
            for file_path in glob.glob(temp_dir_path + "*"):
                age_seconds = self.get_file_age_seconds(file_path)

                if age_seconds > max_age_seconds:
                    os.remove(file_path)
                    num_deleted += 1

        return num_deleted

    ########################################################################
    # Treat these as private functions.
    ########################################################################

    def filter_rows_discrete(self, row_indices, the_filter, data_handle, cc_handle, mccl, ll):
        query_col_coords = list(parse_data_coords([the_filter.column_index], cc_handle, mccl))

        for row_index in row_indices:
            if next(parse_data_values(row_index, ll, query_col_coords, data_handle)).rstrip() in the_filter.values_set:
                yield row_index

    def filter_rows_numeric(self, row_indices, the_filter, operator_dict, data_handle, cc_handle, mccl, ll):
        if the_filter.operator not in operator_dict:
            raise Exception("Invalid operator: " + the_filter.operator)

        query_col_coords = list(parse_data_coords([the_filter.column_index], cc_handle, mccl))

        for row_index in row_indices:
            value = next(parse_data_values(row_index, ll, query_col_coords, data_handle)).rstrip()
            if value == b"": # Is missing
                continue

            # See https://stackoverflow.com/questions/18591778/how-to-pass-an-operator-to-a-python-function
            if operator_dict[the_filter.operator](fastnumbers.float(value), the_filter.query_value):
                yield row_index

    def search_id(self, column_index, search_str=None):
        data_handle = openReadFile(self.data_file_path)
        ll = readIntFromFile(self.data_file_path, ".ll")
        cc_handle = openReadFile(self.data_file_path, ".cc")
        mccl = readIntFromFile(self.data_file_path, ".mccl")
        num_rows = self.num_samples

        col_coords = list(parse_data_coords([column_index], cc_handle, mccl))

        for row_index in range(num_rows):
            value = next(parse_data_values(row_index, ll, col_coords, data_handle)).rstrip().decode()

            if search_str:
                if search_str in value:
                    yield value
            else:
                yield value

        data_handle.close()
        cc_handle.close()

    def parse_values_for_group(self, file_extension, group_name, search_str, max_num):
        values = []

        if os.path.exists(self.data_file_path + file_extension):
            pattern = b"^" + re.escape(group_name).encode() + re.escape(b"\t")

            the_file = openReadFile(self.data_file_path, file_extension)
            for line in iter(the_file.readline, b""):
                if re.search(pattern, line):
                    line_items = line.rstrip(b"\n").split(b"\t")
                    values = self.parse_comma_values(line_items[1].decode(), line_items[2].decode(), search_str, max_num)[:max_num]
                    break

            the_file.close()

        return values

    def parse_comma_values(self, indices_comma_str, values_comma_str, search_str, max_num):
        indices = (int(x) for x in self.isplit(indices_comma_str, ","))
        values = self.isplit(values_comma_str, ",")

        if search_str:
            indices_values = search_indices_values(indices, values, search_str)
        else:
            indices_values = zip(indices, values)

        return list(islice(indices_values, max_num + 1))

    def parse_indices_for_groups(self, file_extension, group_names):
        indices = set()

        if os.path.exists(self.data_file_path + file_extension):
            # my_file = openReadFile(self.data_file_path, file_extension)
            for group_name in group_names:
                my_file = openReadFile(self.data_file_path, file_extension)
                pattern = b"^" + re.escape(group_name).encode() + re.escape(b"\t")
                for line in iter(my_file.readline, b""):
                    if re.search(pattern, line):
                        indices = indices | set([int(x) for x in line.rstrip(b"\n").split(b"\t")[1].split(b",")])

                my_file.close()

        return indices

    def get_variable_description(self, column_index):
        cd_handle = openReadFile(self.data_file_path, ".cd")
        mcdl = readIntFromFile(self.data_file_path, ".mcdl")
        description = next(parse_data_values(column_index, mcdl + 1, [[0, 0, mcdl]], cd_handle)).rstrip().decode()
        cd_handle.close()

        return description

    def get_temp_dir_path(self, sub_dir_name="Geney"):
        return tempfile.gettempdir() + "/" + sub_dir_name + "/"

    def generate_temp_file_path(self):
        sub_dir_path = self.get_temp_dir_path()

        if not os.path.exists(sub_dir_path):
            os.mkdir(sub_dir_path)

        # This checks to make sure the path is unique before returning it (just in case).
        candidate_path = sub_dir_path + next(tempfile._get_candidate_names())
        while os.path.exists(candidate_path):
            candidate_path = sub_dir_path + next(tempfile._get_candidate_names())

        return candidate_path

    def get_file_age_seconds(self, file_path):
        return time.time() - os.path.getmtime(file_path)

    # See https://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python
    def isplit(self, source, sep):
        sepsize = len(sep)
        start = 0
        while True:
            idx = source.find(sep, start)
            if idx == -1:
                yield source[start:]
                return
            yield source[start:idx]
            start = idx + sepsize


if __name__ == '__main__':
    dataset = DataSetParser('/Volumes/KIMBALLUSB/GeneyData/BiomarkerBenchmark_GSE10320/data.fwf')
