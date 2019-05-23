import os
import struct

import numpy as np
from astropy.time import TimeDelta

from .header_handler import bd_header


class DataFile(object):
    def __init__(self, file_path, header_path=None):
        """Parse a MAGDA flatfile at ``file_path``. If ``header_path`` is not
        provided it is assumed that there is a .ffh file colocated
        with the data file.

        """
        self.file_path: str = file_path
        self.header_path = (
            header_path
            if header_path is not None
            else os.path.splitext(file_path)[0] + ".ffh"
        )
        # get information from header file
        metadata = self.parse_header(self.header_path)
        for k, v in metadata.items():
            setattr(self, k, v)

        # read in actual data
        fmt = "".join([c.type_ for c in self.columns])
        row_size = struct.calcsize(fmt)
        with open(self.file_path, "rb") as f:
            b = f.read()

        # some data files contain fewer lines than their
        # headers claim so check the actualy size of the bytes
        # object we get
        actual_n_rows = len(b) // row_size
        if len(b) % row_size:
            raise IOError(
                "Data file does not contain an integer number of rows according"
                " to the expected row length"
            )
        if actual_n_rows != self.n_rows:
            print(
                f"Warning: Datafile {file_path} contains a different number "
                "of rows than indicated in its header file"
            )
            self.n_rows = actual_n_rows
        # breakpoint()
        # ">" denotes the endian or byte significance order of the data
        data = np.array(struct.unpack(">" + (fmt * self.n_rows), b))
        for c in self.columns:
            c.data = data[c.index :: self.n_cols]

        # convert times into objects and rename column for consistency
        # across different header files
        time_column = self.columns[0]
        time_column.data = (
            TimeDelta(time_column.data, format="sec", scale="tai") + self.timebase
        )
        time_column.name = "TIME"

    @staticmethod
    def parse_header(path):
        """Return a dictionary of metadata items from the header file at
        ``path`` describing the contents of a datafile.

        """
        return bd_header(path)

    @property
    def n_cols(self):
        return len(self.columns)

    def __getitem__(self, val):
        try:
            return [c for c in self.columns if c.name == val][0]
        except IndexError:
            raise ValueError(f"No column named {val} in datafile")
