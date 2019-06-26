class DiscreteFilter:
    # Input the column index as an integer.
    # Input the values as a list of strings; will be converted to an encoded set.
    def __init__(self, column_index, values_list):
        self.column_index = column_index
        self.values_set = set([x.encode() for x in values_list])


class NumericFilter:
    # Input the column index as an integer.
    # Operator must be <, <=, >, >=, ==, or !=
    # Query value must numeric (float or int)
    def __init__(self, column_index, operator, query_value):
        self.column_index = column_index
        self.operator = operator
        self.query_value = query_value
