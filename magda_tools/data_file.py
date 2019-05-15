import os
import struct

import numpy as np
from astropy.time import TimeDelta

from binarydata_handler import bd_header

from .header import get_column_info_from_header_file, get_metadata_from_header_file

MAGDA_TYPE_CONVERTER = {"T": "d", "R": "f", "I": "i"}

# To do:
# Check endianness is correct


class DataFile(object):
    def __init__(self, file_path):
        self.file_path: str = file_path
        self.header_file_path = os.path.splitext(file_path)[0] + ".ffh"

        # get information from header file
        metadata = get_metadata_from_header_file(self.header_file_path)
        for k, v in metadata.items():
            setattr(self, k, v)

        self.columns = get_column_info_from_header_file(self.header_file_path)

        # get more complex metadata by parsing via original
        # javascript implementation
        for k, v in bd_header(self.header_file_path).items():
            setattr(self, k, v)

        # read in actual data
        fmt = "".join([MAGDA_TYPE_CONVERTER[c.type_] for c in self.columns])
        with open(self.file_path, "rb") as f:
            # need to be super sure that this is the correct endian!!!
            data = np.array(struct.unpack(">" + (fmt * self.n_rows), f.read()))
        for c in self.columns:
            c.data = data[c.index :: self.n_cols]

        self["TIME_TAI"].data = (
            TimeDelta(self["TIME_TAI"].data, format="sec", scale="tai") + self.timebase
        )

    @property
    def n_cols(self):
        return len(self.columns)

    def __getitem__(self, val):
        try:
            return [c for c in self.columns if c.name == val][0]
        except IndexError:
            raise ValueError(f"No column named {val} in datafile")