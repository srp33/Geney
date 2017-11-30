from .GeneyResponse import GeneyResponse
from fastnumbers import isreal

class JsonResponse(GeneyResponse):
    def __init__(self, dataset, query, gzip_output=False):
        headers = {
            "Content-Disposition": "attachment; filename={}.json".format(dataset.dataset_id)
        }            
        super(JsonResponse, self).__init__(dataset, query, headers, "text/plain", gzip_output)
    
    def generate(self, dataset, query):
        yield '['
        first_row = True
        new_row = True
        col_index = 0
        got_header = False
        header = []
        for items in dataset.get_filtered_data(query):
            if not got_header:
                if items is None:
                    got_header = True
                else:
                    if type(items) is str:
                        header.append(items)
                    else:
                        for item in items:
                            header.append(item)
            else:
                if items is None:
                    yield '}'
                    new_row = True
                    col_index = 0
                else:
                    if type(items) is str:
                        items = [items]

                    for item in items:
                        col_name = header[col_index]
                        col_index += 1
                        if isreal(item):
                            key_val_string = '"{}":{}'.format(col_name, item)
                        else:
                            key_val_string = '"{}":"{}"'.format(col_name, item)
                        if new_row:
                            if first_row:
                                yield '{'
                                first_row = False
                            else:
                                yield ',{'
                            new_row = False
                            yield key_val_string
                        else:
                            yield ',' + key_val_string
        yield ']'