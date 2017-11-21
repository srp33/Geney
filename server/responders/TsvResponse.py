from .GeneyResponse import GeneyResponse

class TsvResponse(GeneyResponse):
    def __init__(self, dataset, query):
        headers = {
            "Content-Disposition": "attachment; filename={}.tsv".format(dataset.dataset_id)
        }            
        super(TsvResponse, self).__init__(dataset, query, headers, 'text/tab-separated-values')
    
    def generate(self, dataset, query):
        new_row = True
        for items in dataset.get_filtered_data(query):
            if items is None:
                yield '\n'
                new_row = True
            else:
                if type(items) is not str:
                    items = '\t'.join(items)

                if new_row:
                    yield items
                    new_row = False
                else:
                    yield '\t' + items