from globals import mpath
from typing import Dict
import os

class File():
    def __init__(self, filename: str, filetype: str, total_chunks: int):
        self.name = filename
        self.type = filetype
        self.total_chunks = total_chunks
        self.data: Dict[int, bytes] = {}
        self.path = ''

        def is_completed(self):
            return len(self.data) == self.total_chunks or os.path.exists(self.path)
        
        def add_chunk(self, chunk_num: int, chunk_data: bytes):
            if chunk_num not in self.data:
                self.data[chunk_num] = chunk_data
            if self.is_completed():
                self.path = mpath(self.name)
                with open(self.path, 'wb') as f:
                    for i in range(self.total_chunks):
                        f.write(self.data[i])
                self.data = {}

        def get_download_progress(self):
            return self.total_chunks / len(self.data)
        
        def open_file(self, path: str):
            if not self.i():
                return
            with open(path, 'wb') as f:
                f.write(self.get_data())
        
        def __repr__(self):
            return f'File: {self.name}'