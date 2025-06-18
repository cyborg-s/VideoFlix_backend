# videoflix/api/utils.py
import os
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse, HttpResponse, Http404


class RangeFileWrapper:
    def __init__(self, file, offset=0, length=None, blksize=8192):
        self.file = file
        self.file.seek(offset)
        self.remaining = length
        self.blksize = blksize

    def __iter__(self):
        while True:
            if self.remaining is not None and self.remaining <= 0:
                break
            data = self.file.read(self.blksize)
            if not data:
                break
            if self.remaining:
                data = data[:self.remaining]
                self.remaining -= len(data)
            yield data
