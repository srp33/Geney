from .GeneyResponse import GeneyResponse

class CsvResponse(GeneyResponse):
    def __init__(self, dataset, query, gzip_output=False):
        gzip_ext = '.gz' if gzip_output else ''
        headers = {
            "Content-Disposition": "attachment; filename={}.csv{}".format(dataset.dataset_id, gzip_ext)
        }            
        super(CsvResponse, self).__init__(dataset, query, headers, "text/plain", gzip_output)
    
    def generate(self, dataset, query):
        new_row = True
        for items in dataset.get_filtered_data(query, [',']):
            if items is None:
                yield '\n'
                new_row = True
            else:
                if type(items) is not str:
                    items = ','.join(items)

                if new_row:
                    yield items
                    new_row = False
                else:
                    yield ',' + items