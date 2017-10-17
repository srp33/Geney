#!flask/bin/python
from flask import Flask, make_response, jsonify, request, Response

# TODO: rename this class
class MyAPI:
    def __init__(self, data_access_obj):
        self.dao = data_access_obj
        self.app = Flask(__name__)
        thing = []
        self.app.add_url_rule('/api/datasets',
                            strict_slashes=False,
                            view_func=self.datasets)
        self.app.add_url_rule('/api/datasets/<string:dataset_id>/meta',
                            strict_slashes=False,
                            view_func=self.meta)
        self.app.add_url_rule('/api/datasets/<string:dataset_id>/meta/<string:meta_type>/search/<string:search>', 
                            strict_slashes=False,
                            view_func=self.search,
                            methods=["GET"])
        self.app.add_url_rule('/api/datasets/<string:dataset_id>/samples',
                            strict_slashes=False,
                            view_func=self.samples,
                            methods=["POST"])
        self.app.add_url_rule('/api/datasets/<string:dataset_id>/download',
                            strict_slashes=False,
                            view_func=self.download,
                            methods=["POST"])
        self.app.add_url_rule('/api/datasets/validate',
                            strict_slashes=False,
                            view_func=self.validate,
                            methods=['GET'])
        self.app.register_error_handler(404, self.not_found)

    def not_found(self, error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    def datasets(self):
        return jsonify(self.dao.get_datasets())

    def meta(self, dataset_id):
        return jsonify(self.dao.get_meta(dataset_id))

    def search(self, dataset_id, meta_type, search):
        if meta_type == "genes":
            return self.gene_search(dataset_id, meta_type, search)
        return self.meta_search(dataset_id, meta_type, search)

    def gene_search(self, dataset_id, meta_type, search):
        return jsonify(self.dao.search_genes(search))

    def meta_search(self, dataset_id, variable, search):
        return jsonify(self.dao.search_meta(variable, search))

    def samples(self, dataset_id):
        print "SAMPLES"
        try:
            posted = request.get_json(force=True)
            print posted
            variables = posted["meta"]
        except:
            return self.not_found(
                'The request was not valid.  Must be JSON with "meta" key.'
            )
        n_samples = self.dao.num_samples(dataset_id, variables)
        return jsonify(n_samples)

    def download(self, dataset_id):
        def generate():
            for i in range(100):
                yield ','.join([c for c in "abcdefghijklmnop"]) + "\n"
        return Response(
            generate(), 
            mimetype='text/csv', 
            headers={
                "Content-Disposition": "attachment; filename=example.csv"
            }
        )
    
    def validate(self):
        dataset_id = request.args.get("val")
        return jsonify(
            self.dao.is_dataset_id_available(dataset_id)
        )


if __name__ == '__main__':
    from data_access import DataObj
    api = MyAPI(DataObj())
    api.app.run(debug=True, host='0.0.0.0', port=9998)