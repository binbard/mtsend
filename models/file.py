from globals import mpath, data_path
from typing import Dict
import os

class File():
    def __init__(self, filename: str, filetype: str, total_chunks: int):
        self.name = filename
        self.type = filetype
        self.total_chunks = total_chunks
        self.size = 0
        self.data: Dict[int, bytes] = {}
        self.path = ''

    def is_completed(self):
        return len(self.data) >= self.total_chunks-1 or self.path != '' and os.path.exists(self.path)
    
    def save_file(self):
        path = data_path(self.name)
        if not self.is_completed():
            return
        with open(path, 'wb') as f:
            for i in range(1, self.total_chunks + 1):
                if i in self.data:
                    f.write(self.data[i])

    def get_left_chunks(self):
        return [i for i in range(1, self.total_chunks + 1) if i not in self.data]
    
    def add_chunk(self, chunk_num: int, chunk_data: bytes):
        if chunk_num not in self.data:
            self.data[chunk_num] = chunk_data

    def get_download_progress(self):
        return self.total_chunks / len(self.data)
    
    def open_file(self, path: str):
        if not self.i():
            return
        with open(path, 'wb') as f:
            f.write(self.get_data())
    
    def __repr__(self):
        return f'File: {self.name}'
    
    @staticmethod
    def from_dict(data: Dict):
        file = File(data['name'], data['type'], data['total_chunks'])
        file.path = data['path']
        file.size = data['size']
        return file
    
    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'total_chunks': self.total_chunks,
            'size': self.size,
            'path': self.path
        }