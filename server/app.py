#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, Response, send_file
from responders.CsvResponse import CsvResponse
from responders.TsvResponse import TsvResponse
from responders.JsonResponse import JsonResponse
import json
from data_access.Dataset import GeneyDataset
import os
DATA_PATH = os.getenv('GENEY_DATA_PATH', '/Users/pjtatlow/projects/web/geney/data/')

RESPONDERS = {
    'tsv': TsvResponse,
    'csv': CsvResponse,
    'json': JsonResponse,
}

DATASETS = {}

for directory in os.listdir(DATA_PATH):
    if os.path.isdir(os.path.join(DATA_PATH, directory)):
        DATASETS[directory] = GeneyDataset(os.path.join(DATA_PATH, directory))

app = Flask(__name__)

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
        query = json.loads(request.form.get('query'))
        if ('options' not in query) or ('fileformat' not in query['options']):
            return bad_request()
        options = query['options']
        query.pop('options')
        file_format = options['fileformat']

        if file_format not in RESPONDERS:
            return bad_request()
        responder = RESPONDERS[file_format]

        return responder(DATASETS[dataset_id], query)
    else:
        return not_found('unknown meta id')


def not_found(error='not found'):
    return make_response(jsonify({'error': "not found"}), 404)

def bad_request(error='bad request'):
    return make_response(jsonify({'error': error}), 400)

app.register_error_handler(404, not_found)

if __name__ == '__main__':

            # print(directory)
    # api = MyAPI(datasets)
    # print(api.not_found(123))
    app.run(debug=True, host='0.0.0.0', port=9998)