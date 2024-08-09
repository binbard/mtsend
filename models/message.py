from models.file import File
from typing import Union

class Message():
    def __init__(self, type: str, content: Union[str, File]):
        self.type = type
        self.content = content

    def __str__(self):
        return f'Message of type {self.type}'