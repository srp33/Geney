import re
# Filename constants
DESCRIPTION_FILE = 'description.json'
DATA_FILE = 'data.pq'
METADATA_DB = 'metadata.sqlite'
METADATA_JSON = 'metadata.json'
GROUPS_JSON = 'groups.json'
REQUIRED_FILES = [DESCRIPTION_FILE, DATA_FILE, GROUPS_JSON]
SAMPLE_COLUMN = "Sample"
HDF5_DATA_PATH = 'data/'


# Meta Type constants
TEXT = 'text'
REAL = 'real'
INTEGER = 'integer'

# Config constants
MAX_OPTIONS = 1000
MAX_ITEMS_IN_OUTPUT_FILE = 500000
SEARCH_LIMIT = 100

# Others
SAMPLE_ID = "sampleID"

# SQL queries
GET_VARIABLE = 'SELECT variableID, variableType FROM variableTable WHERE variableName = ?;'
GET_VARIABLE_OPTIONS = 'SELECT numOptions, options FROM variableTable WHERE variableID = ?;'
GET_ALL_VARIABLE_NAMES = 'SELECT variableName FROM variableTable;'

COUNT_FEATURES = 'SELECT COUNT(*) FROM featureTable;'
GET_FEATURENAMES = 'SELECT featureName from featureTable;'

GET_FEATURE_IDS = 'SELECT featureID, featureName FROM featureTable WHERE featureName IN ({items:s}) ORDER BY featureID ASC;'
GET_ALL_FEATURE_NAMES = 'SELECT featureName FROM featureTable ORDER BY featureID ASC;'
GET_ALL_FEATURE_NAMES = 'SELECT featureName FROM featureTable ORDER BY featureID ASC;'

GET_SAMPLE_NAME = 'SELECT sampleName FROM sampleTable WHERE sampleID = ?;'
GET_SAMPLE_IDS = 'SELECT sampleID FROM sampleTable WHERE sampleName in ({items:s}) ORDER BY sampleID ASC;'
GET_ALL_SAMPLE_IDS = 'SELECT sampleID FROM sampleTable ORDER BY sampleID ASC;'
GET_ALL_SAMPLE_NAMES = 'SELECT sampleName FROM sampleTable;'

SEARCH_FEATURES = 'SELECT DISTINCT featureName FROM featureTable WHERE featureName LIKE ? ORDER BY featureID ASC LIMIT {limit};'.format(limit=SEARCH_LIMIT)
SEARCH_SAMPLES = 'SELECT DISTINCT sampleName FROM sampleTable WHERE sampleName LIKE ? ORDER BY sampleID ASC LIMIT {limit};'.format(limit=SEARCH_LIMIT)
SEARCH_VARIABLES = 'SELECT DISTINCT variableName FROM variableTable WHERE variableName LIKE ? ORDER BY variableID ASC LIMIT {limit};'.format(limit=SEARCH_LIMIT)
SEARCH_TEXT_META_TYPE = 'SELECT DISTINCT value FROM textTable WHERE variableID = ? AND value LIKE ? ORDER BY value ASC LIMIT {limit};'.format(limit=SEARCH_LIMIT)

GET_SAMPLE_TEXT_METADATA = '''
SELECT vt.variableName, tt.value 
  FROM textTable as tt
  INNER JOIN variableTable vt
  ON vt.variableID = tt.variableID 
  WHERE tt.sampleID = ?;
'''
GET_SAMPLE_INTEGER_METADATA = '''
SELECT vt.variableName, it.value 
  FROM integerTable as it
  INNER JOIN variableTable vt
  ON vt.variableID = it.variableID 
  WHERE it.sampleID = ?;
'''

GET_SAMPLE_REAL_METADATA = '''
SELECT vt.variableName, rt.value 
  FROM realTable as rt
  INNER JOIN variableTable vt
  ON vt.variableID = rt.variableID 
  WHERE rt.sampleID = ?;
'''

GET_SAMPLE_METADATA_FROM_TABLE_X = '''
SELECT vt.variableName, x.value 
  FROM {x:s} as x
  INNER JOIN variableTable vt
  ON vt.variableID = x.variableID 
  WHERE x.sampleID = {sample_id:d} 
  AND variableName in ({items:s});
'''

GET_SAMPLEID_TEXT_TABLE = 'SELECT sampleID FROM textTable WHERE variableID = {var_id:d} AND value IN ({items:s});'

GET_SAMPLEID_INTEGER_TABLE = 'SELECT sampleID FROM integerTable WHERE variableID = {var_id:d} AND {where:s};'

GET_SAMPLEID_REAL_TABLE = 'SELECT sampleID FROM realTable WHERE variableID = {var_id:d} AND {where:s};'

DISCRETE_QUERY_REGEX = re.compile('^\s*SELECT\s+sampleID\s+FROM\s+[a-z]+Table\s+WHERE\s+variableID\s+=\s+\d+\s+AND\s+value\s+IN\s+\(("[^";]*",?\s*)*\)\s*;\s*$', re.MULTILINE)
CONTINUOUS_QUERY_REGEX = re.compile('^\s*SELECT\s+sampleID\s+FROM\s+[a-z]+Table\s+WHERE\s+variableID\s+=\s+\d+(\s+AND\s+value\s+(>|>=|<|<=|==|!=)\s+\d+(\.\d*)?)*\s*;\s*$', re.MULTILINE)
