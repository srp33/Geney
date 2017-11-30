from werkzeug.wrappers import Response
import zlib
import struct
import time

class GeneyResponse(Response):
    def __init__(self, dataset, query, headers, mimetype, gzip_output=False):
        response = self.generate(dataset, query)
        if gzip_output == True:
            response = self.gzip(response)
            mimetype = 'application/gzip'

        super(GeneyResponse, self).__init__(response=response, headers=headers, mimetype=mimetype)

    def gzip(self, gen):
        # Shamelessly stolen from this Stackoverflow response: https://stackoverflow.com/questions/44185486/generate-and-stream-compressed-file-with-flask/44387566#44387566
        
        # Yield a gzip file header first.
        yield (
            b'\037\213\010\000' + # Gzip file, deflate, no filename
            struct.pack('<L', int(time.time())) +  # compression start time
            b'\002\377'  # maximum compression, no OS specified
        )

        # bookkeeping: the compression state, running CRC and total length
        compressor = zlib.compressobj(
            9, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
        crc = zlib.crc32(b"")
        length = 0

        for x in gen:
            data = str.encode(x)
            chunk = compressor.compress(data)
            if chunk:
                yield chunk
            crc = zlib.crc32(data, crc) & 0xffffffff
            length += len(data)

        # Finishing off, send remainder of the compressed data, and CRC and length
        yield compressor.flush()
        yield struct.pack("<2L", crc, length & 0xffffffff)        

    def generate(self, dataset, query):
        raise NotImplementedError()