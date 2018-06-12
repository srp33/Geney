#!/usr/bin/env python3

import json
import os
import pickle
import sys
import time
import redis
import re

from flask import Flask, make_response, Response, jsonify, request, send_file
from responders.CsvResponse import CsvResponse
from responders.TsvResponse import TsvResponse
from responders.JsonResponse import JsonResponse
from data_access.Dataset import GeneyDataset
from data_access.Query import Query

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

RESPONDERS = {
    'tsv': TsvResponse,
    'csv': CsvResponse,
    'json': JsonResponse,
}

MIME_TYPES = {
    'csv': 'text/csv',
    'json': 'application/json',
    'tsv': 'text/tsv',
    'gzip': 'application/gzip',
    'html': 'text/html',
    'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'parquet': 'application/parquet',
    'feather': 'application/feather',
    'pickle': 'application/pickle',
    'msgpack': 'application/msgpack',
    'stata': 'application/stata',
    'arff': 'application/arff',
    'sqlite': 'application/sqlite',
    'hdf5': 'application/hdf5'
}

# dictionary of commands and their respective handlers
# each command function registers itself in this dictionary after it is defined
COMMANDS = {}

# cache of datasets so we don't have to go to redis everytime we need a dataset
# if you make a change to a dataset and want it to reload, you'll need to restart the server
# we do not assume this is a comprehansive list of all datasets, for that we rely on redis
DATASETS = {}


app = Flask(__name__)

redis_con = redis.StrictRedis(host='localhost')
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
            except Exception:
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

# @app.route('/api/datasets/<string:dataset_id>/meta', strict_slashes=False)
# @app.route('/api/datasets/<string:dataset_id>/meta/<string:variable_name>', strict_slashes=False)
# def meta(dataset_id, variable_name=None):
#     dataset = get_dataset(dataset_id)
#     if dataset is None:
#         return not_found()
#
#     if variable_name is None: # they're requesting all of the metadata
#         return send_file(dataset.metadata_path)
#     else: # they want the metadata for a specific variable
#         results = dataset.get_variable(variable_name)
#
#         if results is None:
#             return not_found()
#
#         return jsonify(results)

# @app.route('/api/datasets/<string:dataset_id>/meta/<string:meta_type>/search/<string:search_str>', strict_slashes=False)
# @app.route('/api/datasets/<string:dataset_id>/meta/<string:meta_type>/search', strict_slashes=False)
# @app.route('/api/datasets/<string:dataset_id>/meta/search/<string:search_str>', strict_slashes=False)
# @app.route('/api/datasets/<string:dataset_id>/meta/search', strict_slashes=False)
# def search(dataset_id, meta_type='', search_str=''):
#     dataset = get_dataset(dataset_id)
#     if dataset is None:
#         return not_found()
#
#     search_results = dataset.search(meta_type, search_str)
#     if search_results is None:
#         return not_found()
#
#     return jsonify(search_results)

@app.route('/api/datasets/<string:dataset_id>/samples', strict_slashes=False, methods=['POST'])
def count_samples(dataset_id):
    dataset = get_dataset(dataset_id)
    if dataset is None:
        return not_found()

    body = request.get_json()
    count = dataset.get_num_samples_matching_filters(request.get_json())
    if count is None:
        return bad_request()

    return jsonify(count)

@app.route('/api/datasets/<string:dataset_id>/download/', strict_slashes=False, methods=['POST'])
@app.route('/api/datasets/<string:dataset_id>/download/<string:path>', strict_slashes=False, methods=['POST'])
def download(dataset_id, path=None):
    if path:
        dataset = get_dataset(dataset_id)
        if dataset is None:
            return not_found()

        try:
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
        extension = re.search(r'\..*', path).group(0)

        return send_file(os.path.join(DOWNLOAD_LOCATION, path), mimetype=mime_type, as_attachment=True,
                         attachment_filename="{}{}".format(dataset_id, extension))
    else:
        dataset = get_dataset(dataset_id)
        if dataset is None:
            return not_found()

        try:
            query = json.loads(request.form.get('query'))
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

        file_path = dataset.query(query, file_format, gzip_output, DOWNLOAD_LOCATION)
        file_path = file_path.split('/')[-1]
        # extension = re.search(r'\..*', file_path).group(0)
        if file_path:
            return jsonify({'download_path': file_path})
            # return send_file(file_path, mimetype=mime_type, as_attachment=True,
            #                  attachment_filename="{}{}".format(dataset_id, extension))
        else:
            return bad_request()

@app.route('/api/datasets/<string:dataset_id>/link/<string:query_hash>', strict_slashes=False, methods=['GET'])
def use_link(dataset_id, query_hash):
    dataset = get_dataset(dataset_id)
    if dataset is None:
        return not_found()

    try:
        key = '{}_{}'.format(dataset_id, query_hash)
        query = redis_con.get(key)
        if not query:
            return not_found()
        query = json.loads(query.decode("utf-8"))
        return CsvResponse(dataset, query, False)
    except Exception:
        return bad_request()

def not_found(error='not found'):
    return make_response(jsonify({'error': "not found"}), 404)

def bad_request(error='bad request'):
    return make_response(jsonify({'error': error}), 400)


def reload_datasets(params):
    try:
        redis_con.delete('datasets_loaded')
        load_datasets()
        return make_response('success', 200)
    except Exception:
        return make_response('error', 500)

COMMANDS['reload'] = reload_datasets

app.register_error_handler(404, not_found)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9998)
