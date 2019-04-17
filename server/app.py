#!/usr/bin/env python3

import json
import os
import pickle
import sys
import re
import uuid
from psutil import Process as ProcessManager
from psutil import NoSuchProcess
from flask import Flask, make_response, Response, jsonify, request, send_file, send_from_directory
from data_access.Dataset import GeneyDataset
from data_access.filters import DiscreteFilter, NumericFilter
from DataSetParser import DataSetParser
from multiprocessing import Process
from data_access import GeneyJob
import smtplib
from private import EMAIL_PASS, EMAIL_USER
from email.message import EmailMessage

DATA_PATH = os.getenv('GENEY_DATA_PATH', '')
if not DATA_PATH:
	print('"GENEY_DATA_PATH" environment variable not set!', flush=True)
	sys.exit(1)

URL = os.getenv('GENEY_URL', '')
if not URL:
	print('"GENEY_URL" environment variable not set!', flush=True)
	sys.exit(1)

DOWNLOAD_LOCATION = os.getenv('DOWNLOAD_LOCATION', '')
if not DOWNLOAD_LOCATION:
	print('"DOWNLOAD_LOCATION" environment variable not set!', flush=True)
	sys.exit(1)
else:
	DOWNLOAD_HISTORY = os.path.join(DOWNLOAD_LOCATION, 'download_history.pkl')
	with open(DOWNLOAD_HISTORY, 'wb') as fp:
		pickle.dump({}, fp)

MIME_TYPES = {
	'csv': 'text/csv',
	'json': 'application/json',
	'tsv': 'text/tsv',
	'gz': 'application/gzip',
	'html': 'text/html',
	'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
	'pq': 'application/parquet',
	'feather': 'application/feather',
	'pkl': 'application/pickle',
	'msgpack': 'application/msgpack',
	'dta': 'application/stata',
	'arff': 'application/arff',
	'sql': 'application/sqlite',
	'h5': 'application/hdf5',
	'gzip': 'application/gzip',
}

# dictionary of commands and their respective handlers
# each command function registers itself in this dictionary after it is defined
COMMANDS = {}

# cache of datasets so we don't have to go to redis everytime we need a dataset
# if you make a change to a dataset and want it to reload, you'll need to restart the server
# we do not assume this is a comprehansive list of all datasets, for that we rely on redis
DATASETS = {}
DESCRIPTIONS = None
DATASETS_LOADED: bool = False

app = Flask(__name__)


def load_datasets() -> None:
	global DATASETS_LOADED
	global DESCRIPTIONS
	DESCRIPTIONS = {}
	for directory in os.listdir(DATA_PATH):
		if os.path.isdir(os.path.join(DATA_PATH, directory)):
			try:
				dataset = DataSetParser(os.path.join(DATA_PATH, directory, 'data.fwf'))
				DATASETS[dataset.id] = dataset
				DESCRIPTIONS[dataset.id] = dataset.info
			# redis_con.set('dataset_' + directory, pickle.dumps(dataset))
			except Exception as e:
				sys.stderr.write(str(e))
				sys.stderr.write('UNABLE TO LOAD DATASET "{}"'.format(directory))
	DATASETS_LOADED = True


def get_dataset(dataset_id: str) -> DataSetParser:
	try:
		if not DATASETS_LOADED:
			load_datasets()
			return get_dataset(dataset_id)
		if dataset_id in DATASETS:
			return DATASETS[dataset_id]
		else:
			return None
	except Exception:
		return None


@app.route('/api', strict_slashes=False, methods=['POST'])
def geney_command():
	# TODO: add authorization to commands
	params = request.get_json()
	if 'command' not in params:
		return bad_request()

	command = params['command']
	if command not in COMMANDS:
		return bad_request()

	return COMMANDS[command](params)


@app.route('/api/datasets', strict_slashes=False, methods=['GET'])
def get_datasets():
	if not DATASETS_LOADED:
		load_datasets()
	if DESCRIPTIONS is not None:
		return Response(json.dumps(DESCRIPTIONS), mimetype='application/json')
	else:
		return not_found()


@app.route('/api/datasets/<string:dataset_id>/groups', strict_slashes=False)
def get_groups(dataset_id):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	return jsonify(dataset.get_groups())


@app.route('/api/datasets/<string:dataset_id>/groups/<string:group_name>/search', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/groups/<string:group_name>/search/<string:search_str>',
		   strict_slashes=False)
def search_group(dataset_id, group_name, search_str=None):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	return jsonify(dataset.search_group(group_name, search_str))


@app.route('/api/datasets/<string:dataset_id>/options', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/options/<int:column_index>', strict_slashes=False)
def get_options(dataset_id, column_index=None):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	if column_index:
		results = dataset.get_variable_meta(column_index)
		return jsonify(results)
	else:
		# return send_file(dataset.options_path)
		return not_found()


@app.route('/api/datasets/<string:dataset_id>/options/<int:column_index>/search', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/options/<int:column_index>/search/<string:search_str>',
		   strict_slashes=False)
def search_options(dataset_id, column_index, search_str=None):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	else:
		return jsonify(dataset.search_variable_options(column_index, search_str))


@app.route('/api/datasets/<string:dataset_id>/samples', strict_slashes=False, methods=['POST'])
def get_samples(dataset_id):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	filters = json.loads(request.data)
	numeric_filters = []
	discrete_filters = []
	for column_index in filters.keys():
		column_values = filters[column_index]['value']
		if type(column_values[0]) == dict:
			for column_value in column_values:
				numeric_filters.append(NumericFilter(int(column_index), column_value['operator'], column_value['value']))
		else:
			discrete_filters.append(DiscreteFilter(int(column_index), column_values))
	count, file = dataset.save_sample_indices_matching_filters(discrete_filters, numeric_filters)
	return jsonify({'count': count, 'sampleFile': file})


@app.route('/api/datasets/<string:dataset_id>/columns', strict_slashes=False, methods=['POST'])
def get_columns(dataset_id):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	query = json.loads(request.data)
	groups = query['groups']
	features = [int(x) for x in query['features']]
	num_columns, col_indices_file, col_names_file = dataset.save_column_indices_to_select(features, groups, [])
	return jsonify(
		{'numColumns': num_columns, 'columnIndicesFile': col_indices_file, 'columnNamesFile': col_names_file})


@app.route('/api/datasets/<string:dataset_id>/download', strict_slashes=False, methods=['POST'])
def create_download(dataset_id):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	query = json.loads(request.data)
	row_indices_file = query['sampleFile']
	col_indices_file = query['columnIndicesFile']
	col_names_file = query['columnNamesFile']
	file_name = '{}-{}.tsv'.format(dataset_id, uuid.uuid4().hex[:8])
	file_path = os.path.join(DOWNLOAD_LOCATION, file_name)
	dataset.build_output_file(row_indices_file, col_indices_file, col_names_file, file_path, 'tsv')
	return jsonify({'downloadPath': file_name})


@app.route('/api/datasets/<string:dataset_id>/num_points', strict_slashes=False, methods=['POST'])
def num_points(dataset_id):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	params = request.get_json()
	groups = params['groups']
	features = params['features']
	samples = params['num_samples']
	return jsonify({'num_data_points': dataset.get_num_data_points(samples, groups, features)})


@app.route('/api/data/status/<string:path>', strict_slashes=False, methods=['GET'])
def download(path):
	file_type = path.split('.')[-1]
	if file_type == 'gz':
		file_type = path.split('.')[-2]
	path = os.path.join(DOWNLOAD_LOCATION, path)
	if os.path.exists(path):
		return jsonify({'url': '/api/data/download/{}'.format(path.split('/')[-1])})
	else:
		return jsonify({'status': 'incomplete'})


@app.route('/api/data/download/<string:path>', strict_slashes=False, methods=['GET'])
def get(path):
	file_type = path.split('.')[-1]
	if file_type == 'gz':
		file_type = path.split('.')[-2]
	mime_type = MIME_TYPES[file_type]
	extension = re.search(r'\..*', path).group(0)
	full_path = os.path.join(DOWNLOAD_LOCATION, path)
	if os.path.exists(full_path):
		# return send_file(full_path, mimetype=mime_type, as_attachment=True,
		#                  attachment_filename="{}{}".format(path.split('-')[0], extension))
		return send_from_directory(DOWNLOAD_LOCATION, path, mimetype=mime_type, as_attachment=True,
								   attachment_filename="{}{}".format(path.split('-')[0], extension))
	else:
		return not_found()


@app.route('/api/data/cancel/<string:path>', strict_slashes=False, methods=['GET'])
def cancel_download(path):
	if os.path.exists(DOWNLOAD_HISTORY):
		with open(DOWNLOAD_HISTORY, 'rb') as fp:
			download_history = pickle.load(fp)
	else:
		print('Problem managing processes...')
	if path in download_history.keys():
		pid = download_history[path].pid
		try:
			p = ProcessManager(pid)
			if p.is_running():
				p.kill()
		except NoSuchProcess as e:
			print(e)
	if os.path.exists(os.path.join(DOWNLOAD_LOCATION, '{}incomplete'.format(path))):
		os.remove(os.path.join(DOWNLOAD_LOCATION, '{}incomplete'.format(path)))
	if os.path.exists(os.path.join(DOWNLOAD_LOCATION, path)):
		os.remove(os.path.join(DOWNLOAD_LOCATION, path))
	return jsonify({'status': 'success'})


@app.route('/api/data/notify/<string:path>', strict_slashes=False, methods=['POST'])
def notify(path):
	email = request.form.get('email')
	name = request.form.get('name')
	if os.path.exists(DOWNLOAD_HISTORY):
		with open(DOWNLOAD_HISTORY, 'rb') as fp:
			download_history = pickle.load(fp)
	if path not in download_history.keys():
		return not_found('No job found')
	else:
		download_history[path].email = email
		download_history[path].name = name
		with open(DOWNLOAD_HISTORY, 'wb') as fp:
			pickle.dump(download_history, fp)
	if os.path.exists(os.path.join(DOWNLOAD_LOCATION, path)):
		send_email(path, email, name)
	return jsonify({'status': 'success'})


@app.route('/api/datasets/<string:dataset_id>/query/', strict_slashes=False, methods=['POST'])
def query(dataset_id):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()

	try:
		query = request.form.get('query')
		options = json.loads(request.form.get('options'))
	except Exception:
		return bad_request()

	if 'fileformat' not in options:
		return bad_request()

	file_format = options['fileformat']

	gzip_output = options['gzip'] if ('gzip' in options) else False

	if gzip_output:
		mime_type = MIME_TYPES['gzip']
	else:
		mime_type = MIME_TYPES[file_format]

	# TODO: Validate query before starting response
	filename = '{}-{}'.format(dataset_id, uuid.uuid4().hex[:8])
	if file_format == 'csv':
		filename += ".csv"
	elif file_format == 'json':
		filename += ".json"
	elif file_format == 'pickle':
		filename += '.pkl'
	elif file_format == 'tsv':
		filename += '.tsv'
	elif file_format == 'hdf5':
		filename += '.h5'
	elif file_format == 'arff':
		filename += '.arff'
	elif file_format == 'excel':
		filename += '.xlsx'
	elif file_format == 'feather':
		filename += '.feather'
	elif file_format == 'msgpack':
		filename += '.msgpack'
	elif file_format == 'parquet':
		filename += '.pq'
	elif file_format == 'stata':
		filename += '.dta'
	elif file_format == 'sqlite':
		filename += '.sql'
	elif file_format == 'html':
		filename += '.html'
	else:
		filename += ".csv"
	if gzip_output:
		filename += '.gz'

	p = Process(target=create_dataset, args=(dataset, query, file_format, gzip_output, DOWNLOAD_LOCATION, filename))
	p.start()
	if os.path.exists(DOWNLOAD_HISTORY):
		with open(DOWNLOAD_HISTORY, 'rb') as fp:
			download_history = pickle.load(fp)
	else:
		download_history = {}
	with open(DOWNLOAD_HISTORY, 'wb') as fp:
		download_history[filename] = GeneyJob(p.pid, filename)
		pickle.dump(download_history, fp)
	return jsonify({'download_path': filename})


def not_found(error='not found'):
	return make_response(jsonify({'error': str(error)}), 404)


def bad_request(error='bad request'):
	return make_response(jsonify({'error': error}), 400)


def reload_datasets():
	global DATASETS_LOADED
	try:
		DATASETS_LOADED = False
		load_datasets()
		return make_response('success', 200)
	except Exception:
		return make_response('error', 500)


def create_dataset(dataset: GeneyDataset, query, file_format, gzip_output, download_location, filename):
	dataset.query(query, file_format, gzip_output, download_location, filename)
	if os.path.exists(DOWNLOAD_HISTORY):
		with open(DOWNLOAD_HISTORY, 'rb') as fp:
			download_history = pickle.load(fp)
		if filename in download_history.keys():
			if download_history[filename].email is not None:
				send_email(filename, download_history[filename].email, download_history[filename].name)
	else:
		print('problem with history')


def send_email(path, email, name):
	s = smtplib.SMTP(host='smtp.gmail.com', port=587)
	s.starttls()
	s.login(EMAIL_USER, EMAIL_PASS)
	subject = 'Geney Data Complete'
	path = '{}/api/data/download/{}'.format(URL, path)

	message = EmailMessage()
	message['From'] = 'Geney'
	message['To'] = email
	message['Subject'] = subject
	message.set_content('{},\nThank you for your patience! Here is your data: {}'.format(name, path))

	s.send_message(message)


COMMANDS['reload'] = reload_datasets

app.register_error_handler(404, not_found)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8889)
