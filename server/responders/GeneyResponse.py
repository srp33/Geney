from werkzeug.wrappers import Response

class GeneyResponse(Response):
    def __init__(self, dataset, query, headers, mimetype):
        
        super(GeneyResponse, self).__init__(self.generate(dataset, query), headers=headers, mimetype=mimetype)

    def generate(self, dataset, query):
        raise NotImplementedError()