import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from secrets import token_hex

class Storage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            dir_name, file_name = os.path.split(name)
            file_root, file_ext = os.path.splitext(file_name) 
            my_chars = token_hex(2)

            name = os.path.join(dir_name, '{}_{}{}'.format(file_root, my_chars, file_ext))
        return name
        