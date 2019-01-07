#!/usr/bin/env python3

import json
import os
import pickle
import sys
import redis
import re
import uuid
from psutil import Process as ProcessManager
from psutil._exceptions import NoSuchProcess
from flask import Flask, make_response, Response, jsonify, request, send_file, send_from_directory
from data_access.Dataset import GeneyDataset
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

app = Flask(__name__)

redis_con = redis.StrictRedis(host='redis')
redis_con.flushdb()


def load_datasets() -> None:
	# do not load datasets if they're already loaded!
	if redis_con.get('datasets_loaded') is not None:
		return
	if redis_con.get('datasets_loading') is not None:
		return
	# set lock so no other workers try to load datasets at the same time
	redis_con.set('datasets_loading', True)
	descriptions = {}
	for directory in os.listdir(DATA_PATH):
		if os.path.isdir(os.path.join(DATA_PATH, directory)):
			try:
				dataset = GeneyDataset(os.path.join(DATA_PATH, directory))
				DATASETS[dataset.dataset_id] = dataset
				descriptions[dataset.dataset_id] = dataset.description
				redis_con.set('dataset_' + directory, pickle.dumps(dataset))
			except Exception as e:
				sys.stderr.write(str(e))
				sys.stderr.write('UNABLE TO LOAD DATASET "{}"'.format(directory))
	# set the descriptions in the redis, so we don't calculate it everytime
	descriptions_str = json.dumps(descriptions)
	redis_con.set('dataset_descriptions', descriptions_str)
	# set datasets_loaded key so we don't try to load them again
	redis_con.set('datasets_loaded', True)
	# unlock
	redis_con.delete('datasets_loading')


def get_dataset(dataset_id: str) -> GeneyDataset:
	try:
		if dataset_id in DATASETS:
			return DATASETS[dataset_id]
		if not datasets_loaded():
			load_datasets()
			return get_dataset(dataset_id)
		dataset_def = redis_con.get('dataset_' + dataset_id)
		if dataset_def is None:
			return None
		dataset = pickle.loads(dataset_def)
		DATASETS[dataset_id] = dataset
		return dataset
	except Exception:
		return None


def datasets_loaded() -> bool:
	loaded = redis_con.get('datasets_loaded')
	print('Checking if datasets loaded', loaded, loaded is not None)
	return loaded is not None


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
	if not datasets_loaded():
		load_datasets()
	descriptions = redis_con.get('dataset_descriptions')
	if descriptions is not None:
		return Response(descriptions, mimetype='application/json')
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
@app.route('/api/datasets/<string:dataset_id>/options/<string:variable_name>', strict_slashes=False)
def get_options(dataset_id, variable_name=None):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	if variable_name:
		results = dataset.get_variable(variable_name)
		return jsonify(results)
	else:
		return send_file(dataset.options_path)


@app.route('/api/datasets/<string:dataset_id>/options/<string:variable_name>/search', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/options/<string:variable_name>/search/<string:search_str>',
		   strict_slashes=False)
def search_options(dataset_id, variable_name, search_str=None):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	else:
		return jsonify(dataset.search_options(variable_name, search_str))


@app.route('/api/datasets/<string:dataset_id>/samples', strict_slashes=False, methods=['POST'])
def count_samples(dataset_id):
	dataset = get_dataset(dataset_id)
	if dataset is None:
		return not_found()
	count = dataset.get_num_samples_matching_filters(request.data)
	if count is None:
		return bad_request()

	return jsonify(count)


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
		# print(request.form.get('email'), request.form.get('name'))
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


@app.route('/api/datasets/<string:dataset_id>/link/<string:query_hash>', strict_slashes=False, methods=['GET'])
def use_link(dataset_id, query_hash):
	# TODO: create hash of queries
	return bad_request()
	# dataset = get_dataset(dataset_id)
	# if dataset is None:
	# 	return not_found()
	#
	# try:
	# 	key = '{}_{}'.format(dataset_id, query_hash)
	# 	query = redis_con.get(key)
	# 	if not query:
	# 		return not_found()
	# 	query = json.loads(query.decode("utf-8"))
	# 	return CsvResponse(dataset, query, False)
	# except Exception:
	# 	return bad_request()


def not_found(error='not found'):
	return make_response(jsonify({'error': error}), 404)


def bad_request(error='bad request'):
	return make_response(jsonify({'error': error}), 400)


def reload_datasets(params):
	try:
		redis_con.delete('datasets_loaded')
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
