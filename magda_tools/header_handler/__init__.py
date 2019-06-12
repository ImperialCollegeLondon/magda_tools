"""Classes and functions related to handling binary data files."""

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from string import Template

import numpy as np
from astropy.time import Time

BDDIR = os.path.dirname(os.path.abspath(__file__))
HEADER_COMMAND_TEMPLATE = Template(f"java -jar {BDDIR}/HeaderFileParser.jar $ffd_path")
MAGDA_TYPE_CONVERTER = {
    "class java.lang.Double": "d",
    "class java.lang.Float": "f",
    "class java.lang.Integer": "i",
}
MAGDA_NAME_ATTRIBUTE_REGEX = (
    r"mrdcd_(?P<telem>hk|sd|sh)(?P<sensor>fgm|vhm|shm)(?:n|c)?"
    r"_(?P<coord>c|krtp|kso|ksm|kg|tiis|enis|iais|j3|jmxyz|gse|gsm|rtn|sc)"
    r"(?:_(?P<res>ssd|\d{1,2}[ms]))?"
)

MAGDA_TIME_FMT = "%Y %j %b %d %H:%M:%S"
MAGDA_TIME_FMT_MS = MAGDA_TIME_FMT + ".%f"


def command_executor(command):
    """Executes ``command`` in external process and returns stdout if successful
    otherwise raises subprocess.SubprocessError containing stderr.
    """
    try:
        cp = subprocess.run(  # blocking call
            command.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise subprocess.SubprocessError(e.stderr.decode(sys.getfilesystemencoding()))
    return cp.stdout.decode(sys.getfilesystemencoding()).strip()


def bd_header(dataset):
    """Blocking call of BinaryDataJoiner java code in external process to
    construct ``VirtualMagdaDataFile`` specified by ``dataset``.
    :param dataset: valid ``VirtualMagdaDataFile`` dataset name (str).
    :returns: named tuple containing data from header file
    """

    command = HEADER_COMMAND_TEMPLATE.substitute({"ffd_path": dataset})
    stdout = command_executor(command)
    metadata = {}
    metadata["columns"] = []

    for line in stdout.split("\n"):
        label, value = line.split("=")
        if label == "timebase":
            metadata[label] = Time(
                int(value) / 1000, format="unix", scale="tai"
            )  # astropy time object for convenience
        elif label.startswith("column"):
            vals = value.split(",")
            args = (
                [int(label.replace("column", ""))]
                + vals[:-1]
                + [MAGDA_TYPE_CONVERTER[vals[-1]]]
            )
            metadata["columns"].append(Column(*args))
        elif label == "attrs":
            path_metadata = re.match(MAGDA_NAME_ATTRIBUTE_REGEX, value).groupdict()
            metadata.update(
                {
                    "res": path_metadata["res"] if path_metadata["res"] else "",
                    "sensor": path_metadata["sensor"].upper(),
                    "coord": path_metadata["coord"].upper(),
                    "telem": path_metadata["telem"].upper(),
                }
            )
        elif label in ("start", "end"):
            metadata[label] = datetime.strptime(value, MAGDA_TIME_FMT_MS)
        elif label == "n_rows":
            metadata[label] = int(value)

    # The C coordinate system is a bit different and should never
    # contain a BTotal column although this is added by default
    # by the JavaHeaderParser
    if metadata["coord"] == "C":
        metadata["columns"] = metadata["columns"][:-1]
    return metadata


@dataclass
class Column:
    index: int
    name: str
    source: str
    units: str
    type_: str
    data: np.array = np.array([])
