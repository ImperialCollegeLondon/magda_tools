import os


class DataFileParser(object):
    def __init__(self, file_path):
        self.file_path: str = file_path
        self.header_file_path = os.path.splitext(file_path)[0] + ".ffh"

        self.parse_header()
