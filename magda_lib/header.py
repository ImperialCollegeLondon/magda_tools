"""For the time being this has been copied directly from the magda
repository eventually this should become the canonical version."""

from datetime import datetime
import os
import re
from string import Template
from textwrap import wrap

CASDATA = os.environ["CASDATA"]

MAGDA_FFH_TEXTWIDTH = 72
MAGDA_DATA_FILE_REGEX = (
    r"(?P<start_date>\d{5})_mrdcd_(?P<telem>hk|sd|sh)"
    r"(?P<sensor>fgm|vhm|shm)(?:n|c)?_"
    r"(?P<coord>c|krtp|kso|ksm|kg|tiis|enis|iais|j3|jmxyz|gse|gsm|rtn|sc)"
    r"(?:_(?P<res>ssd|\d{1,2}[ms]))?"
)

MAGDA_PATH_REGEX_TEMPLATE = Template(
    r"${casdata}/y\d{2}\/\d{5}\/processed\/%s[.]${ext}" % MAGDA_DATA_FILE_REGEX
)
MAGDA_HEADER_PATH_REGEX = MAGDA_PATH_REGEX_TEMPLATE.substitute(
    casdata=CASDATA, ext="ffh"
)

MAGDA_TIME_FMT = "%Y %j %b %d %H:%M:%S"
MAGDA_TIME_FMT_MS = MAGDA_TIME_FMT + ".%f"


def get_metadata_from_header_file(ffh):
    """Return dict containing metadata from header file, ``ffh``.
    """
    with open(ffh, "r") as f:
        s = f.read()
    lines = wrap(
        s, MAGDA_FFH_TEXTWIDTH
    )  # .ffh contains no new lines so needs to be wrapped

    metadata = {}

    metadata["calibrated"] = "calibrated"  # Assume all data calibrated

    # telemetry, coord. system, resolution, and sensor available from path
    path_metadata = re.match(MAGDA_HEADER_PATH_REGEX, ffh).groupdict()

    metadata.update(
        {
            "res": path_metadata["res"] if path_metadata["res"] else "",
            "sensor": path_metadata["sensor"].upper(),
            "coord": path_metadata["coord"].upper(),
            "telem": path_metadata["telem"].upper(),
        }
    )

    # Extract start and end times from header file
    for l in lines:
        if l.startswith("FIRST TIME"):
            metadata["start"] = l.split("=")[1].strip(" \0")
        if l.startswith("LAST TIME"):
            metadata["end"] = l.split("=")[1].strip(" \0")

    # Set last_modified date based on mtime from filesystem
    ffd = os.path.splitext(ffh)[0] + ".ffd"
    most_recent_mtime = max(os.path.getmtime(ffh), os.path.getmtime(ffd))
    metadata["last_modified"] = datetime.utcfromtimestamp(most_recent_mtime).strftime(
        MAGDA_TIME_FMT_MS
    )
    return metadata
