#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, Response, send_file
from responders.CsvResponse import CsvResponse
from responders.TsvResponse import TsvResponse
from responders.JsonResponse import JsonResponse
from data_access.Dataset import GeneyDataset
from data_access.Query import Query

import json
import os, sys
import redis


DATA_PATH = os.getenv('GENEY_DATA_PATH', '')
if len(DATA_PATH) == 0:
    print('"GENEY_DATA_PATH" environment variable not set!')
    sys.exit(1)

URL = os.getenv('GENEY_URL', '')
if len(URL) == 0:
    print('"GENEY_URL" environment variable not set!')
    sys.exit(1)

RESPONDERS = {
    'tsv': TsvResponse,
    'csv': CsvResponse,
    'json': JsonResponse,
}

DATASETS = {}

for directory in os.listdir(DATA_PATH):
    if os.path.isdir(os.path.join(DATA_PATH, directory)):
        try:
            DATASETS[directory] = GeneyDataset(os.path.join(DATA_PATH, directory))
        except Exception:
            sys.stderr.write('UNABLE TO LOAD DATASET "{}"'.format(directory))

app = Flask(__name__)

Redis = redis.StrictRedis(host='redis')

@app.route('/api/datasets', strict_slashes=False)
def get_datasets():
    return jsonify({dataset_id: dataset.description for dataset_id, dataset in DATASETS.items()})
    
@app.route('/api/datasets/<string:dataset_id>/meta', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/meta/<string:variable_name>', strict_slashes=False)
def meta(dataset_id, variable_name=None):
    if dataset_id not in DATASETS:
        return not_found('unknown meta id')

    if variable_name is None: # they're requesting all of the metadata
        return send_file(DATASETS[dataset_id].metadata_path)
    else: # they want the metadata for a specific variable
        results = DATASETS[dataset_id].get_variable(variable_name)

        if results is None:
            return not_found()

        return jsonify(results)
        

@app.route('/api/datasets/<string:dataset_id>/meta/<string:meta_type>/search/<string:search_str>', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/meta/<string:meta_type>/search', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/meta/search/<string:search_str>', strict_slashes=False)
@app.route('/api/datasets/<string:dataset_id>/meta/search', strict_slashes=False)
def search(dataset_id, meta_type='', search_str=''):
    if dataset_id not in DATASETS:
        return not_found('unknown meta id')
    
    search_results = DATASETS[dataset_id].search(meta_type, search_str)
    if search_results is None:
        return not_found()

    return jsonify(search_results)    

@app.route('/api/datasets/<string:dataset_id>/samples', strict_slashes=False, methods=['POST'])
def count_samples(dataset_id):
    if dataset_id in DATASETS:
        return jsonify(DATASETS[dataset_id].get_num_samples_matching_filters(request.get_json()))
    else:
        return not_found('unknown meta id')        

@app.route('/api/datasets/<string:dataset_id>/download', strict_slashes=False, methods=['POST'])
def download(dataset_id):
    if dataset_id in DATASETS:
        try:
            query = json.loads(request.form.get('query'))
            options = json.loads(request.form.get('options'))
        except Exception:
            return bad_request()
        
        if 'fileformat' not in options:
            return bad_request()

        file_format = options['fileformat']

        if file_format not in RESPONDERS:
            return bad_request()

        gzip_output = options['gzip'] if ('gzip' in options) else False

        # TODO: Validate query before starting response

        responder = RESPONDERS[file_format]

        return responder(DATASETS[dataset_id], query, gzip_output)
    else:
        return not_found('unknown dataset id')

@app.route('/api/datasets/<string:dataset_id>/link', strict_slashes=False, methods=['POST'])
def generate_link(dataset_id):
    if dataset_id in DATASETS:
        try:
            query_str = request.get_json()
            query = Query(query_str, DATASETS[dataset_id].description)
            Redis.set('{}_{}'.format(dataset_id, query.md5), json.dumps(query_str))
            return jsonify({
                'link': '{base}/api/datasets/{dataset}/link/{hash}'.format(base=URL,dataset=dataset_id, hash=query.md5)
            })
        except Exception:
            return bad_request()        
        # return jsonify()
    else:
        return not_found('unknown dataset id')

@app.route('/api/datasets/<string:dataset_id>/link/<string:query_hash>', strict_slashes=False, methods=['GET'])
def use_link(dataset_id, query_hash):
    if dataset_id in DATASETS:
        try:
            key = '{}_{}'.format(dataset_id, query_hash)
            query = Redis.get(key)
            if not query:
                return not_found()
            query = json.loads(query.decode("utf-8"))
            return CsvResponse(DATASETS[dataset_id], query, False)
        except Exception:
            return jsonify('foo')
            return bad_request()        
    else:
        return not_found('unknown dataset id')

def not_found(error='not found'):
    return make_response(jsonify({'error': "not found"}), 404)

def bad_request(error='bad request'):
    return make_response(jsonify({'error': error}), 400)

app.register_error_handler(404, not_found)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9998)