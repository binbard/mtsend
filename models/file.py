from typing import Dict

class File():
    def __init__(self, filename: str, filetype: str, total_chunks: int):
        self.name = filename
        self.type = filetype
        self.total_chunks = total_chunks
        self.data: Dict[int, bytes] = {}

        def is_complete(self):
            return len(self.data) == self.total_chunks
        
        def add_chunk(self, chunk_num: int, chunk_data: bytes):
            self.data[chunk_num] = chunk_data

        def get_data(self):
            return b''.join([self.data[i] for i in range(self.total_chunks)])
        
        def __repr__(self):
            return f'File: {self.name}'