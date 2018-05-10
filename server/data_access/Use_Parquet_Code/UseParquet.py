import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import xlsxwriter
from sqlalchemy import create_engine
from .ColumnInfo import ColumnInfo
from .ContinuousQuery import ContinuousQuery
from .DiscreteQuery import DiscreteQuery
from .OperatorEnum import OperatorEnum
from .FileTypeEnum import FileTypeEnum
import sys

def peek(parquetFilePath, numRows=10, numCols=10)->pd.DataFrame:
	
	allCols = getColumnNames(parquetFilePath)
	if(numCols>len(allCols)):
		numCols=len(allCols)
	selectedCols = []
	selectedCols.append("Sample")
	for i in range(0, numCols):
		selectedCols.append(allCols[i])
	df = pd.read_parquet(parquetFilePath, columns=selectedCols)
	df.set_index("Sample", drop=True, inplace=True)
	df=df.iloc[0:numRows, 0:numCols]
	return df

def columnsPyarrow(parquetFilePath, numRows=10, numCols=10):
	table= pq.read_table(parquetFilePath)
	columns = list(table.schema)
	return columns

def peekByColumnNames(parquetFilePath, listOfColumnNames,numRows=10)->pd.DataFrame:
	listOfColumnNames.insert(0,"Sample")
	df = pd.read_parquet(parquetFilePath, columns=listOfColumnNames)
	df.set_index("Sample", drop=True, inplace=True)
	df=df[0:numRows]
	return df

def getColumnNames(parquetFilePath)->list:
	"""
	Returns a list of all column names from a given parquet dataset
	"""
	
	p = pq.ParquetFile(parquetFilePath)
	columnNames = p.schema.names
	#delete 'Sample' from schema
	del columnNames[0]

	#delete extraneous other schema that the parquet file tacks on at the end
	if '__index_level_' in columnNames[len(columnNames)-1]:
		del columnNames[len(columnNames)-1]
	if 'Unnamed:' in columnNames[len(columnNames)-1]:
		del columnNames[len(columnNames)-1]
	return columnNames

def getColumnInfo(parquetFilePath, columnName:str, sizeLimit:int=None)->ColumnInfo:
	"""
	Given a parquet file and column name, returns a ColumnInfo object describing the column's name,data type (discrete/continuous), and all its unique values	
	"""
	columnList = [columnName]
	df = pd.read_parquet(parquetFilePath, columns=columnList)
	uniqueValues = set()
	counter =0
	for index, row in df.iterrows():
		uniqueValues.add(row[columnName])
		counter+=1
		if sizeLimit != None:
			if counter>=sizeLimit:
				break
	uniqueValues = list(uniqueValues)
	if isinstance(uniqueValues[0],str):
		return ColumnInfo(columnName,"discrete", uniqueValues)
	else:
		return ColumnInfo(columnName, "continuous", uniqueValues)

def query(parquetFilePath, columnList: list=[], continuousQueries: list=[], discreteQueries: list=[])->pd.DataFrame:
	"""
	Performs mulitple queries on a parquet dataset. If no queries or columns are passed, it returns the entire dataset as a pandas dataframe
	"""
	if len(columnList)==0 and len(continuousQueries)==0 and len(discreteQueries)==0:
		df = pd.read_parquet(parquetFilePath)
		df.set_index("Sample", drop=True, inplace=True)
		return df
	
	#extract all necessary columns in order to read them into pandas
	for query in continuousQueries:
		columnList.append(query.columnName)
	for query in discreteQueries:
		if query.columnName not in columnList:
			columnList.append(query.columnName)
	columnList.insert(0,"Sample")
	df = pd.read_parquet(parquetFilePath, columns = columnList)
	df.set_index("Sample", drop=True, inplace=True)
	del columnList[0]

	#perform continuous queries, adjusting for which operator is to be used
	for query in continuousQueries:
		if query.operator == OperatorEnum.Equals:
			df = df.loc[df[query.columnName]==query.value, [ col for col in columnList]]
		elif query.operator == OperatorEnum.GreaterThan:
			df = df.loc[df[query.columnName]>query.value, [ col for col in columnList]]
		elif query.operator == OperatorEnum.GreaterThanOrEqualTo:
			df = df.loc[df[query.columnName]>=query.value, [ col for col in columnList]]
		elif query.operator == OperatorEnum.LessThan:
			df = df.loc[df[query.columnName]<query.value, [ col for col in columnList]]
		elif query.operator == OperatorEnum.LessThanOrEqualTo:
			df = df.loc[df[query.columnName]<=query.value, [ col for col in columnList]]
	#perform discrete queries
	for query in discreteQueries:
		df = df.loc[df[query.columnName].isin(query.values), [col for col in columnList]]
	
	return df

def exportQueryResults(parquetFilePath, outFilePath, outFileType:FileTypeEnum, columnList: list=[], continuousQueries: list=[], discreteQueries: list=[]):
	"""Wrapper function for query that exectues queries then exports them to the given file type, such as JSON or CSV
	"""
	df = query(parquetFilePath, columnList, continuousQueries, discreteQueries)
	if outFileType== FileTypeEnum.CSV:
		df.to_csv(path_or_buf=outFilePath, sep='\t')
	elif outFileType == FileTypeEnum.JSON:
		df.to_json(path_or_buf=outFilePath)
	elif outFileType == FileTypeEnum.Excel:
		writer = pd.ExcelWriter(outFilePath, engine='xlsxwriter')
		df.to_excel(writer, sheet_name='Sheet1') 
		writer.save()
	elif outFileType == FileTypeEnum.Feather:
		df=df.reset_index()
		df.to_feather(outFilePath)
	elif outFileType ==FileTypeEnum.HDF5:
		df.to_hdf(outFilePath, "group", mode= 'w')
	elif outFileType ==FileTypeEnum.MsgPack:
		df.to_msgpack(outFilePath)
	elif outFileType ==FileTypeEnum.Parquet:
		df.to_parquet(outFilePath)
	elif outFileType == FileTypeEnum.Stata:
		df.to_stata(outFilePath)
	elif outFileType == FileTypeEnum.Pickle:
		df.to_pickle(outFilePath)

