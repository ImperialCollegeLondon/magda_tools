from dataclasses import dataclass
from datetime import datetime
import os
import re
from typing import Any, Dict, Union

import numpy as np
from astropy.time import Time, TimeDelta

COLUMN_REGEX = re.compile(
    r"(?P<index>[0-9]{3})\s+(?P<name>[A-Z,a-z,0-9,_,/,(,)]{1,10})(\s+)?(?P<units>[a-z,A-Z]+)"
    r"\s+(?P<source>[a-z,A-Z,_]+(\s[a-z,A-Z,_]+)?)\s+(?P<type>[I,R,T])\s+(?P<loc>[0-9]+)"
)

MAGDA_NAME_ATTRIBUTE_REGEX = re.compile(
    r"mrdcd_(?P<telem>hk|sd|sh)(?P<sensor>fgm|vhm|shm)(?:n|c)?"
    r"_(?P<coord>c|krtp|kso|ksm|kg|tiis|enis|iais|j3|jmxyz|gse|gsm|rtn|sc)"
    r"(?:_(?P<res>ssd|\d{1,2}[ms]))?"
)

MAGDA_TIME_FMT = "%Y %j %b %d %H:%M:%S"
MAGDA_TIME_FMT_MS = MAGDA_TIME_FMT + ".%f"

EPOCHS = dict(J2000=946727968, Y1958=-378691200, Y1966=-126230400)

DATA_TYPES = {"T": "d", "R": "f", "I": "i"}


@dataclass
class Column:
    index: int
    name: str
    source: str
    units: str
    type_: str
    data: np.array = np.array([])


class DataFile(object):
    def __init__(self, file_path: str, header_path: str = None):
        """Parse a MAGDA flatfile at ``file_path``. If ``header_path`` is not
        provided it is assumed that there is a .ffh file colocated
        with the data file.

        """
        self.file_path = file_path
        self.header_path = (
            header_path
            if header_path is not None
            else os.path.splitext(file_path)[0] + ".ffh"
        )
        # get information from header file
        metadata = self.parse_header(self.header_path)
        self.n_rows = metadata["n_rows"]
        self.columns = metadata["columns"]
        self.timebase = metadata["timebase"]
        self.coord = metadata["coord"]
        self.sensor = metadata["sensor"]
        self.start = metadata["start"]
        self.end = metadata["end"]
        self.telem = metadata["telem"]
        self.res = metadata["res"]

        # read in actual data
        dt = np.dtype([(c.name, ">" + c.type_) for c in self.columns])
        with open(self.file_path, "rb") as f:
            data = np.fromfile(f, dt)

        # some data files contain fewer lines than their
        # headers claim so check the actual array size
        actual_n_rows = len(data)
        if actual_n_rows != self.n_rows:
            print(
                f"Warning: Datafile {file_path} contains a different number "
                "of rows than indicated in its header file"
            )
            self.n_rows = actual_n_rows

        for c in self.columns:
            c.data = data[c.name]

        # convert times into objects and rename column for consistency
        # across different header files
        time_column = self.columns[0]
        time_column.data = (
            TimeDelta(time_column.data, format="sec", scale="tai") + self.timebase
        )
        time_column.name = "TIME"

        if self.coord == "C":
            # decode raw sensor status data into a status value indicating
            # the sensitivity range in which the sensor is operating
            sensor_status = self[f"{self.sensor}Status"]
            sensor_status.data = self.decode_sensor_status(sensor_status.data)

    @staticmethod
    def parse_header(path: str) -> Dict[str, Any]:
        """Return a dictionary of metadata items from the header file at
        ``path`` describing the contents of a datafile.
        """
        metadata: Dict[str, Any] = {"columns": []}

        lines = []
        with open(path) as f:
            while True:
                line = f.read(72)
                if line:
                    lines.append(line)
                else:
                    break

        for line in lines:
            match = COLUMN_REGEX.search(line)
            if match:
                groups = match.groupdict()
                column = Column(
                    int(groups["index"].lstrip("0")) - 1,
                    groups["name"],
                    groups["source"],
                    groups["units"],
                    DATA_TYPES[groups["type"]],
                )
                metadata["columns"].append(column)
            elif line.startswith(("LAST TIME", "FIRST TIME")):
                value = line.split(" = ")[1].strip()
                value = " ".join(value.split())
                if value.startswith("9"):
                    value = "19" + value
                key = "end" if line.startswith("LAST TIME") else "start"
                metadata[key] = datetime.strptime(value, MAGDA_TIME_FMT_MS)
            elif line.startswith("NROWS"):
                metadata["n_rows"] = int(line.split(" = ")[1].strip())
            elif line.startswith("EPOCH"):
                timebase = int(EPOCHS[line.split(" = ")[1].strip()])
                metadata["timebase"] = Time(timebase, format="unix", scale="utc")

        match = MAGDA_NAME_ATTRIBUTE_REGEX.search(str(path))
        if match is not None:
            path_metadata = match.groupdict()
            metadata.update(
                {
                    "res": path_metadata["res"] if path_metadata["res"] else "",
                    "sensor": path_metadata["sensor"].upper(),
                    "coord": path_metadata["coord"].upper(),
                    "telem": path_metadata["telem"].upper(),
                }
            )

        return metadata

    @property
    def n_cols(self):
        return len(self.columns)

    def __getitem__(self, val: str) -> Column:
        try:
            return [c for c in self.columns if c.name == val][0]
        except IndexError:
            raise ValueError(f"No column named {val} in datafile")

    @staticmethod
    def decode_sensor_status(status: Union[np.ndarray, int]) -> Union[np.ndarray, int]:
        """Decode raw sensor status information into a status code. ``status``
        can be a number of sequence of numbers.
        """
        status = np.array(status)
        return np.right_shift(np.bitwise_and(status.astype(int), 0xC0000000), 30)
